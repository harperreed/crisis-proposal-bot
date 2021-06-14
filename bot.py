from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
import os

import json
import time
import hashlib

from pprint import pprint


def object_hash(object_to_hash):
  str = json.dumps(object_to_hash)
  return hashlib.sha224(str.encode('utf-8')).hexdigest()

  

def save_state(state):
  path = os.path.dirname(os.path.realpath(__file__))
  json_filename = path + "/bot-state.json"
  
  with open(json_filename, 'w') as outfile:
    json.dump(state, outfile, sort_keys=True, indent=4)
  
    # transaction_data = json.load(json_file)

def get_state():
  path = os.path.dirname(os.path.realpath(__file__))
  json_filename = path + "/bot-state.json"
  if (os.path.isfile(json_filename)):
    with open(json_filename) as json_file:
      return json.load(json_file)
  else:
    return {}

def gqlQuery(query, variables):
  # Select your transport with a defined url endpoint
  snapshot_graphql_url = "https://hub.snapshot.org/graphql"
  transport = AIOHTTPTransport(url=snapshot_graphql_url)

  # Create a GraphQL client using the defined transport
  client = Client(transport=transport, fetch_schema_from_transport=True)

  query = gql(query)
  # Execute the query on the transport
  result = client.execute(query, variable_values=variables)
  return result

def grab_proposals(space, first, state):
  # Select your transport with a defined url endpoint

  query = """query Proposals($first: Int!, $skip: Int!, $state: String!, $space: String, $space_in: [String], $author_in: [String]) {
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
  
  params = {
      "first":first,
      "skip":0,
      "space":space,
      "state":state,
      "author_in":[]
    }

  # Execute the query on the transport
  result = gqlQuery(query, params)
  return result

def grab_proposal_votes(proposal):
  # this isn't helpful cuz we don't get token count
  query = """query Votes( $proposal: String!,) {      votes(

        where: {proposal: $proposal}
      ) {
          id
        voter
        created
        choice
        metadata
      }
    }"""
  params = {
      "proposal":proposal['id'],
    }

  # Execute the query on the transport
  result = gqlQuery(query, params)
  votes = []
  votes_response = result['votes']
  for v in votes_response:
    v['choice_text'] = proposal['choices'][v['choice']-1]

    votes.append(v)
  return votes


def send_webhook(proposal):
  webhook_url = os.environ['DISCORD_WEBHOOK_URL']
  webhook = DiscordWebhook(url=webhook_url)
  # infura_app_id = os.environ['INFURA_APP_ID']
  # infura_url = "https://mainnet.infura.io/v3/" +infura_app_id

  # ens = ENS(Web3.HTTPProvider(infura_url))

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

# result = grab_proposals("crisisdao.eth", 2, "all")

bot_state = get_state()

try:
  last_update = bot_state['last_update']
except:
  last_update = 0
  pass


if ((int(time.time()-last_update))>300):
  result = grab_proposals("crisisdao.eth", 5, "all")
  
  if ('notifications' not in bot_state):
    bot_state['notifications'] =  {}
  for p in result['proposals']:
    proposal_hash = object_hash(p)
    if (p['id'] in bot_state['notifications']):
      if (proposal_hash!=bot_state['notifications'][p['id']]['hash']):
        bot_state['notifications'][p['id']]['hash'] = proposal_hash
        bot_state['notifications'][p['id']]['sent'] = False
    else:
      bot_state['notifications'][p['id']] = {"hash": proposal_hash, "sent": False}

    # votes = grab_proposal_votes(p)
    # pprint(votes)
    # p['active_notification']
    if 'proposals' not in bot_state:
      bot_state['proposals'] = {}
    
    bot_state['proposals'][p['id']] = p
    
    
    # send_webhook(p)
  for n in bot_state['notifications']:
    
    if (bot_state['notifications'][n]['sent'] == False):
      send_webhook( bot_state['proposals'][n])
      bot_state['notifications'][n]['sent'] = True
  bot_state['last_update'] = int(time.time())
  save_state(bot_state)



# for p in result['proposals']:
#   pprint(p)
#   # votes = grab_proposal_votes(p)
#   # pprint(votes)
#   print("---")
#   send_webhook(p)



# infura_app_id = os.environ['INFURA_APP_ID']
# infura_url = "https://mainnet.infura.io/v3/" +infura_app_id

# w3 =Web3.HTTPProvider(infura_url)


# if (w3.isConnected()):
#   ns = ENS.fromWeb3(w3)

# # domain = ns.name('0xc93C7f71581DFEAAb59BEd908888dAC5689F312a')
# # print(domain)