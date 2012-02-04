#!/usr/bin/python

import gdata.docs as gdocs
import gdata.docs.service as gservice

job = 'james.obeirne@gmail.com'

def client(user=job, pwd=''):
  gd_client = gservice.DocsService(source='auburn-miser-v1')
  gd_client.ClientLogin(user, pwd)

  return gd_client

def get_sheets(client):
  feed = client.GetDocumentListFeed()
  sheets = filter(lambda e: e.GetDocumentType() == "spreadsheet",
                  feed.entry)

  print '\n'
  for sheet in sheets:
    ent_str = "%s - %s" % (sheet.title.text, sheet.resourceId.text)
    print ent_str


