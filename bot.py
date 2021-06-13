from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from discord_webhook import DiscordWebhook, DiscordEmbed

from web3 import Web3
from ens.auto import ns
from pprint import pprint


def grab_proposals(space, first, state):
  # Select your transport with a defined url endpoint
  transport = AIOHTTPTransport(url="https://hub.snapshot.org/graphql")

  # Create a GraphQL client using the defined transport
  client = Client(transport=transport, fetch_schema_from_transport=True)

  query = gql(
      """query Proposals($first: Int!, $skip: Int!, $state: String!, $space: String, $space_in: [String], $author_in: [String]) {
        proposals(
          first: $first
        skip: $skip
        where: {space: $space, state: $state, space_in: $space_in, author_in: $author_in}
      ) {
          id
        title
        body
        start
        end
        state
        author
        
        __typename
      }
    }"""
  )
  params = {
      "first":first,
      "skip":0,
      "space":space,
      "state":state,
      "author_in":[]
    }

  # Execute the query on the transport
  result = client.execute(query, variable_values=params)
  return result

def send_webhook(proposal):
  webhook_url = ""
  webhook = DiscordWebhook(url=webhook_url)

  ens = ENS(Web3.HTTPProvider("https://mainnet.infura.io/v3/"))


  # create embed object for webhook
  embed = DiscordEmbed(title=proposal['title'], description=proposal['body'], color='03b2f8')

  author = proposal['author']
  author_url = "https://art.pizza/" + author
  domain = ens.name(proposal['author'])
  
  print(domain)
  if domain:
    author = domain

  embed.set_author(name=author, url=author_url, icon_url='https://avatars0.githubusercontent.com/u/14542790')
  embed.set_footer(text='Embed Footer Text')
  embed.set_timestamp()
  embed.add_embed_field(name='Status', value=proposal['state'])
  embed.add_embed_field(name='Start', value=proposal['start'])
  embed.add_embed_field(name='End', value=proposal['end'])
  

  webhook.add_embed(embed)

  response = webhook.execute()

# result = grab_proposals("crisisdao.eth", 4, "all")



# for p in result['proposals']:
#   pprint(p)
#   print("---")
#   send_webhook(p)


w3 =Web3.HTTPProvider("https://mainnet.infura.io/v3/443ec86ea6ae445ea1499a403e14e899")



domain = ns.name('0xc93C7f71581DFEAAb59BEd908888dAC5689F312a')
print(domain)