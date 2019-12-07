# API Documentation

This module provides objects for keeping data 'relatively' safe
from change during a program.

Often we pass data/collections around a program that we don't want changed without our knowledge by another part of the program. The intention behind the classes in this module is to avoid inadvertent data tampering. It's NOT intended to prevent hacking the data by those who know how.

Boxes can be locked to stop their contents being amended.
Although a BoxList (stores the box's contents) inherits from the 
bog-standard Python list object many attributes have been disabled. 
For instance you cannot natively assign to a box. Instead you use 
special methods for storage ('put') and retrieval. 

**let's create some items for content** \
myset = set([3,7,9,23,True]) \
fibonacci = [0,1,1,2,3,5,8,13,21,34] \
sq_primes = ((1,1), (3,9), (5,25), (7,49), (11,121)) \
authors = { \
    'Shakespeare' : 'As You Like It', \
    'Hemingway' : 'The Old Man And The Sea', \
    'Atwood': "The Handmaid's Tale", \
    'Angelou': 'I Know Why The Caged Bird Sings', \
} \
song = 'Redemption Song'

**Create box - new boxes are open by default** \
**keywords required but only 'key' is compulsory** \
b = Box(key='secret', name="new box")

**add items to box** \
b.put(myset, 'myset')         # named content \
b.put([1,2,3], 'simples') \
b.put(fibonacci) \
b.put(sq_primes) \
b.put(authors)

**mutables are deepcopied before being added to box** \
**so this won't actually update something in the box** \
authors['Sontag'] = 'On Photography'

**locking the box stops contents from being added or removed** \
b.lock('secret') \
b.put(song)                 # fails \
b.put(song, key='secret')   # add key to open; stays open \
b.open('secret')            # alternative: open box and then put new item

**set, delete, rename items** \
b.getnames() # returns tuples of (name, type) \
b.setname(2, 'setname') # index, new name; only for items without names \
b.rename('setname', 'renamed') # current name, new name \
b.delname('renamed') # deletes name association but not the item

**delete an item in the box** \
b.destroy(name=myset)       # fails because should be string \
b.destroy(name='simples')   # destroy by item name \
b.destroy(item=sq_primes)   # destroy by variable name \
b.destroy(index='1')        # fails because should be integer \
b.destroy(index=1)          # destroy by index

**removes and returns an item from the box** \
**using index here** \
fetched = b.fetch(index=1) # get second item

**return an item from the box without removing it** \
**nb. changes to item will be reflected in the box** \
using = b.use(name='myset') \
using.add('using item') \
using = b.use(index=0) \
using.add('using index')

**empty box contents** \
b.empty()

**check status - these return True or False** \
b.isopen \
b.isempty \
b.contains(authors)
