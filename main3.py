import discord
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain.document_loaders import WebBaseLoader
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory


# Configuration des clés API
#DISCORD_TOKEN = "MTI2MDIzOTk4NTYwMTI4NjI3MA.GuqOg0.F9neq_vSXodA0DmMGWZLOj_lL78pKwnBkDZd38"
#HUGGINGFACE_TOKEN = "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"

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def load_document(url):
    loader = WebBaseLoader(url)
    return loader.load()

def load_documents():
    base_url = "https://warcrier.net/docs/"
    page_urls = [
        "intro/", "getting-started/", "getting-started/bespoke-warbands/",
        # ... (rest of the URLs)
        "rules/", "rules/battleplan/", "rules/fighting-the-battle/", "rules/move-actions/", "rules/attack-actions/",
        "rules/other-actions/", "rules/abilities/", "rules/reactions/", "rules/objectives-and-treasure-tokens/",
        "rules/allies-thralls-and-monsters/",
        "rules/runemarks/", "rules/faction-runemarks/", "rules/bladeborn/", "rules/designers-commentary/",
        "rules/terrain/", "rules/terrain/gnarlwood-terrain-special-rules/",
        "rules/terrain/scales-of-talaxis-terrain-rules/",
        "rules/varanite-delve-special-rules/", "rules/terrain/dungeon-terrain/", "rules/optional-rules/",

        "warbands/", "warbands/chaos/allies-of-chaos/", "warbands/chaos/monsters-of-chaos/",
        "warbands/chaos/thralls-of-chaos/",
        "warbands/chaos/beasts-of-chaos/", "warbands/chaos/beasts-of-chaos/background-tables/",
        "warbands/chaos/blades-of-khorne-bloodbound/",
        "warbands/chaos/blades-of-khorne-bloodbound/background-tables", "warbands/chaos/blades-of-khorne-daemons/",
        "warbands/chaos/chaos-legionnaires/", "warbands/chaos/chaos-legionnaires/background-tables",
        "warbands/chaos/chaos-legionnaires/quests",
        "warbands/chaos/claws-of-karanak/", "warbands/chaos/claws-of-karanak/quests/",
        "warbands/chaos/claws-of-karanak/background-tables",
        "warbands/chaos/corvus-cabal/", "warbands/chaos/corvus-cabal/quests",
        "warbands/chaos/corvus-cabal/background-tables",

        "warbands/chaos/cypher-lords/", "warbands/chaos/cypher-lords/background-tables/",
        "warbands/chaos/cypher-lords/community-gallery/",
        "warbands/chaos/darkoath-savagers/", "warbands/chaos/darkoath-savagers/background-tables/",
        "warbands/chaos/disciples-of-tzeentch-arcanites/",
        "warbands/chaos/disciples-of-tzeentch-arcanites/background-tables/",
        "warbands/chaos/disciples-of-tzeentch-daemons/",
        "warbands/chaos/hedonites-of-slaanesh-daemons/", "warbands/chaos/hedonites-of-slaanesh-sybarites/",
        "warbands/chaos/hedonites-of-slaanesh-sybarites/background-tables/", "warbands/chaos/horns-of-hashut/",
        "warbands/chaos/horns-of-hashut/quests/",
        "warbands/chaos/horns-of-hashut/background-tables/", "warbands/chaos/iron-golem/",
        "warbands/chaos/iron-golem/background-tables/",
        "warbands/chaos/jade-obelisk/", "warbands/chaos/jade-obelisk/quests/",
        "warbands/chaos/jade-obelisk/background-tables/",

        "warbands/chaos/maggotkin-of-nurgle-daemons/", "warbands/chaos/maggotkin-of-nurgle-rotbringers/",
        "warbands/chaos/maggotkin-of-nurgle-rotbringers/background-tables/",
        "warbands/chaos/rotmire-creed/", "warbands/chaos/rotmire-creed/quests/",
        "warbands/chaos/rotmire-creed/background-tables/", "warbands/chaos/scions-of-the-flame/",
        "warbands/chaos/scions-of-the-flame/background-tables/", "warbands/chaos/skaven/",
        "warbands/chaos/skaven/background-tables/",
        "warbands/chaos/slaves-to-darkness/", "warbands/chaos/slaves-to-darkness/background-tables/",
        "warbands/chaos/spire-tyrants/",
        "warbands/chaos/spire-tyrants/background-tables/", "warbands/chaos/splintered-fang/",
        "warbands/chaos/splintered-fang/background-tables/",
        "warbands/chaos/tarantulos-brood/", "warbands/chaos/tarantulos-brood/background-tables/",
        "warbands/chaos/the-unmade/",
        "warbands/chaos/the-unmade/background-tables/", "warbands/chaos/untamed-beasts/",
        "warbands/chaos/untamed-beasts/background-tables/",
        "warbands/chaos/untamed-beasts/community-gallery/",

        "warbands/death/monsters-of-death/", "warbands/death/thralls-of-death/", "warbands/death/askurgan-trueblades/",
        "warbands/death/askurgan-trueblades/quests/", "warbands/death/askurgan-trueblades/background-tables/",
        "warbands/death/flesh-eater-courts/",
        "warbands/death/flesh-eater-courts/background-tables/", "warbands/death/flesh-eater-courts/community-gallery/",
        "warbands/death/nighthaunt/", "warbands/death/nighthaunt/background-tables/",
        "warbands/death/ossiarch-bonereapers/",
        "warbands/death/ossiarch-bonereapers/background-tables/", "warbands/death/pyregheists/",
        "warbands/death/royal-beastflayers/",
        "warbands/death/royal-beastflayers/quests/", "warbands/death/royal-beastflayers/background-tables/",
        "warbands/death/soulblight-gravelords/", "warbands/death/soulblight-gravelords/quests/",
        "warbands/death/soulblight-gravelords/background-tables/",
        "warbands/death/teratic-cohorts/",

        "warbands/destruction/monsters-of-destruction/", "warbands/destruction/thralls-of-destruction/",
        "warbands/destruction/bonesplitterz/"
        "warbands/order/monsters-of-order/", "warbands/destruction/bonesplitterz/background-tables/",
        "warbands/destruction/gloomspite-gitz/",
        "warbands/destruction/gloomspite-gitz/background-tables/", "warbands/destruction/gloomspite-gitz/the-bad-moon/",
        "warbands/destruction/gloomspite-gitz/quests/", "warbands/destruction/gobbapalooza/",
        "warbands/destruction/gorger-mawpack/",
        "warbands/destruction/gorger-mawpack/quests/", "warbands/destruction/gorger-mawpack/background-tables/",
        "warbands/destruction/ironjawz/", "warbands/destruction/ironjawz/background-tables/",
        "warbands/destruction/ironjawz/community-gallery/",
        "warbands/destruction/kruleboyz/", "warbands/destruction/kruleboyz/background-tables/",
        "warbands/destruction/kruleboyz-monsta-killaz/",
        "warbands/destruction/kruleboyz-monsta-killaz/quests/",
        "warbands/destruction/kruleboyz-monsta-killaz/background-tables/",
        "warbands/destruction/ogor-mawtribes/", "warbands/destruction/ogor-mawtribes/background-tables/",

        "warbands/order/allies-of-order/", "warbands/order/monsters-of-order/", "warbands/order/blacktalons/",
        "warbands/order/cities-of-sigmar/",
        "warbands/order/cities-of-sigmar-castelite-hosts/", "warbands/order/cities-of-sigmar-castelite-hosts/quests",
        "warbands/order/cities-of-sigmar-castelite-hosts/background-tables",
        "warbands/order/cities-of-sigmar-castelite-hosts/dawnbringers/"
        "warbands/order/cities-of-sigmar-darkling-covens/", "warbands/order/cities-of-sigmar-dispossessed/",
        "warbands/order/daughters-of-khaine/"
        "warbands/order/fyreslayers/", "warbands/order/hunters-of-huanchi/",
        "warbands/order/hunters-of-huanchi/quests/",
        "warbands/order/idoneth-deepkin/", "warbands/order/idoneth-deepkin/quests/",
        "warbands/order/khainite-shadowstalkers/",
        "warbands/order/kharadron-overlords/", "warbands/order/lumineth-realm-lords/", "warbands/order/order-of-azyr/",

        "warbands/order/seraphon/", "warbands/order/stormcast-eternals-questor-soulsworn/",
        "warbands/order/stormcast-eternals-questor-soulsworn/quests",
        "warbands/order/stormcast-eternals-sacrosanct-chamber/",
        "warbands/order/stormcast-eternals-thunderstrike-stormcasts/",
        "warbands/order/stormcast-eternals-vanguard-auxiliary-chamber/",
        "warbands/order/stormcast-eternals-warrior-chamber/",
        "warbands/order/sylvaneth/", "warbands/order/twistweald/", "warbands/order/vulkyn-flameseekers/",
        "warbands/order/vulkyn-flameseekers/quests/", "warbands/order/wildercorps-hunters/",
        "warbands/order/wildercorps-hunters/quests",
        "warbands/order/ydrilan-riverblades/",

        "battles/open-play/", "battles/open-play/coalition-of-death/",
        "battles/open-play/coalition-of-death/clash-of-might/",
        "battles/open-play/coalition-of-death/camp-raid/", "battles/open-play/triumph-and-treachery/",
        "battles/open-play/triumph-and-treachery/there-can-be-only-one/",
        "battles/open-play/triumph-and-treachery/lord-of-the-tower/",
        "battles/matched-play/", "battles/narrative-play/creating-a-warband-roster/",
        "battles/narrative-play/fighting-campaign-battles/",
        "battles/narrative-play/the-aftermath-sequence/", "battles/narrative-play/quests/",
        "battles/narrative-play/campaign-arcs/",
        "battles/narrative-play/the-sundered-scales/", "battles/narrative-play/before-the-gnarlwood/",
        "battles/narrative-play/before-the-gnarlwood/challenge-battles/",
        "battles/narrative-play/before-the-gnarlwood/narrative-battles/", "battles/running-a-warcry-tournament/",
        "battles/battleplan-generator/", "battles/battleplan-generator/deployment-maps",
        "battles/battleplan-generator/victory-conditions/",
        "battles/battleplan-generator/twists/",

        "releases",

    ]

    prompt_template = """Vous êtes un assistant spécialisé dans les règles du jeu Warcrier. 
        Utilisez le contexte suivant pour répondre à la question de manière concise et précise. 
        Si vous ne pouvez pas répondre à la question en vous basant uniquement sur le contexte fourni, dites-le clairement.

    """

    documents = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(load_document, base_url + page): page for page in page_urls}
        for future in as_completed(future_to_url):
            documents.extend(future.result())

    return documents

def setup_rag(documents):
    repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        max_length=128,
        temperature=0.5,
        huggingfacehub_api_token=HUGGINGFACE_TOKEN,
    )

    embeddings = HuggingFaceEmbeddings()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    texts = text_splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(documents=texts, embedding=embeddings)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    )

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        return_generated_question=False,
    )

    return qa_chain

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print("Chargement des documents...")
    documents = load_documents()
    print(f"{len(documents)} pages chargées.")
    print("Configuration du système RAG...")
    global qa_chain
    qa_chain = setup_rag(documents)
    print("Système RAG prêt.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == "warcrier":
        try:
            await message.channel.send("Recherche de la réponse...")
            response = qa_chain({"question": message.content})['answer']
            await message.reply(f"{response}", mention_author=True)
        except Exception as e:
            await message.channel.send(f"Une erreur s'est produite : {str(e)}")

    await bot.process_commands(message)

@bot.command(name='Warcry')
async def warcry(ctx, *, question):
    try:
        await ctx.send("Recherche de la réponse...")
        response = qa_chain({"question": question})['answer']
        await ctx.reply(f"{response}", mention_author=True)
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite : {str(e)}")

bot.run(DISCORD_TOKEN)