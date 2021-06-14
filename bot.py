from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
import os
from web3 import Web3
from ens import ENS


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
        created


        choices
        snapshot
        
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
        created


        choices
        snapshot
        
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
  webhook_url = os.environ['DISCORD_WEBHOOK_URL']
  webhook = DiscordWebhook(url=webhook_url)
  infura_app_id = os.environ['INFURA_APP_ID']
  infura_url = "https://mainnet.infura.io/v3/" +infura_app_id

  ens = ENS(Web3.HTTPProvider(infura_url))

  title = proposal['state'].upper() + ": " + proposal['title']

  # create embed object for webhook
  embed = DiscordEmbed(title=title, description=proposal['body'], color='03b2f8')

  author = proposal['author']
  author_url = "https://art.pizza/" + author
  author_avatar_url = "https://avatar-party.web.app/a/" + author + ".png"
  # domain = ens.name(proposal['author'])
  
  # print(domain)
  # if domain:
  #   author = domain
  embed.set_url("https://vote.crisis.network/#/crisisdao.eth/proposal/" + proposal['id'])
  embed.set_author(name=author, url=author_url, icon_url=author_avatar_url)
  embed.set_footer(text='CrisisDao Snapshot Bot')

  embed.set_timestamp()

  date_format = '%c'
  
  start_date = datetime.utcfromtimestamp(int(proposal['start'])).strftime(date_format)
  end_date = datetime.utcfromtimestamp(int(proposal['end'])).strftime(date_format)
  created = datetime.utcfromtimestamp(int(proposal['created'])).strftime(date_format)

  embed.add_embed_field(name='Status', value=proposal['state'])
  embed.add_embed_field(name='Snapshot', value=proposal['snapshot'])
  embed.add_embed_field(name='Created', value=created)
  embed.add_embed_field(name='Start', value=start_date)
  embed.add_embed_field(name='End', value=end_date)

  

  webhook.add_embed(embed)

  response = webhook.execute()

result = grab_proposals("crisisdao.eth", 2, "all")



for p in result['proposals']:
  pprint(p)
  print("---")
  send_webhook(p)


# infura_app_id = os.environ['INFURA_APP_ID']
# infura_url = "https://mainnet.infura.io/v3/" +infura_app_id

# w3 =Web3.HTTPProvider(infura_url)


# if (w3.isConnected()):
#   ns = ENS.fromWeb3(w3)

# # domain = ns.name('0xc93C7f71581DFEAAb59BEd908888dAC5689F312a')
# # print(domain)