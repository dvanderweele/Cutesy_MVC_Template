from .helpers.cutify import handleCuteness
import sys

def run():
  if len(sys.argv) > 2: 
    # cutesy command line service handler
    if sys.argv[1] == 'cutify':
      handleCuteness(sys.argv[2])
    