import urllib, os, orjson
from datetime import datetime
import time
from urllib.request import urlopen
from urllib.error import HTTPError
import pandas as pd
import numpy as np

def parse_threads(threads: list) -> dict:
  print(f'Parsing threads ...')
  results = {}
  for thread in threads:
    try:
      url = f'https://a.4cdn.org/pol/thread/{thread}.json'
      r = urlopen(url)
      data = orjson.loads(r.read())
      comments = {}
      for comment in range(len(data['posts']))[1:]:
        comments[data['posts'][comment]['no']] = {
            'name': data.get('posts')[comment].get('name'),
            'comment': data.get('posts')[comment].get('com'),
            'time': data.get('posts')[comment].get('time'),
            'country': data.get('posts')[comment].get('country')
        }

      results[thread] = {
          'name': data.get('posts')[0].get('name'),
          'subject': data.get('posts')[0].get('sub'),
          'comment': data.get('posts')[0].get('com'),
          'time': data.get('posts')[0].get('time'),
          'country': data.get('posts')[0].get('country'),
          'replies': data.get('posts')[0].get('replies'),
          'comments': comments
      }
    except HTTPError:
      continue

  print(f'Parsing complete')
  return results


def scrape_4chan(board: str, archive: bool = False) -> dict:
  threads = []

  if archive:
    print(f'Gathering archived threads from 4Chan/{board}/ ...')
    url = f'https://a.4cdn.org/{board}/archive.json'
    r = urlopen(url)
    data = orjson.loads(r.read())
    for thread in range(len(data)):
      threads.append(thread)

  else:
    print(f'Gathering threads from 4Chan/{board}/ ...')
    url = f'https://a.4cdn.org/{board}/catalog.json'
    r = urlopen(url)
    data = orjson.loads(r.read())
    for i in range(len(data)):
      for j in range(len(data[i]['threads'])):
        threads.append(data[i]['threads'][j]['no'])

  print(f'Found {len(threads)} threads.')
  results = parse_threads(threads)
  return results

def all_4chan_to_csv(board: str, directory: str | os.PathLike = os.getcwd()) -> None:
  active_results = scrape_4chan(board)
  print(f'Active threads: {len(active_results)}')
  archive_results = scrape_4chan(board, archive=True)
  print(f'Archive threads: {len(archive_results)}')
  results = {**archive_results, **active_results}
  print(f'Total threads: {len(results)}')

  all_comments = {}
  for thread_id, thread_data in active_results.items():
  # Add the main post of the thread (its 'no' is the thread_id itself)
    all_comments[thread_id] = {
        'name': thread_data.get('name'),
        'comment': thread_data.get('comment'),
        'time': datetime.fromtimestamp(thread_data.get('time')),
        'country': thread_data.get('country'),
        'thread': thread_id, # Reference the thread ID
        'subject': thread_data.get('subject'), # Use 'sub' for subject based on data structure
        'threadtime': datetime.fromtimestamp(thread_data.get('time')) # Time of the main post
    }

    # Add all individual comments (replies) within the thread
    # thread_data['comments'] is a dictionary where keys are comment numbers and values are comment details
    if 'comments' in thread_data and thread_data['comments']:
      for comment_id, comment_data in thread_data['comments'].items():
        all_comments[comment_id] = {
            'name': comment_data.get('name'),
            'comment': comment_data.get('comment'),
            'time': datetime.fromtimestamp(comment_data.get('time')),
            'country': comment_data.get('country'),
            'thread': thread_id, # Reference the parent thread ID
            'subject': thread_data.get('subject'), # Inherit subject from parent thread
            'threadtime': datetime.fromtimestamp(thread_data.get('time')) # Time of the main post
        }
  print(f'Total comments: {len(all_comments)}')
  df = pd.DataFrame.from_dict(all_comments, orient='index')
  df.to_csv(f'{directory}/{board}_{datetime.now().date()}.csv')
  print(f'Saved to {directory}/{board}_{datetime.now().date()}.csv')


