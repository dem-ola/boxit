# API Documentation

This module provides objects for keeping data 'relatively' safe
from change during a program.

Often we pass data/collections around a program that we don't want changed without our knowledge by another part of the program. The motivation for the classes in this module is to avoid inadvertent data tampering. It's NOT intended to prevent hacking the data by those who know how.

### Basics
Python base objects (strings, lists etc) can be stored in boxes. \
Boxes can be stored in crates. \
Crates can be stored in Containers.

Boxes, crates and containers are vessels. \
Vessels can be locked to stop their contents being amended. \
Vessels and python object items can be named. Names must be unique and the same item cannot be stored in more than one vessel. 


**Let's create some items for content**
```
myset = set([3,7,9,23,True])
fibonacci = [0,1,1,2,3,5,8,13,21,34]
sq_primes = ((1,1), (3,9), (5,25), (7,49), (11,121))
authors = { \
    'Shakespeare' : 'As You Like It',
    'Hemingway' : 'The Old Man And The Sea',
    'Atwood': "The Handmaid's Tale",
    'Angelou': 'I Know Why The Caged Bird Sings',
}
song = 'Redemption Song'
```

**Create vessels - new vessels are open by default** \
**Keywords required but only 'key' is compulsory**
```
b = Box(key='secret', name="new box")
c = Crate(key='secret')             # no name given; set to None
```

**Add items to box** \
**You can add the same object more than once if given a different name**
```
b.put(myset)                        # un-named item; name set to None
b.put(myset, 'myset2')              # named item
b.put(myset, 'myset2', 'secret')    # named item with key in case vessel is locked
b.put([1,2,3], 'simples')
b.put(fibonacci)                    
b.put(sq_primes)
b.put(authors)

# more complex examples
# we put a new Box with no name inside a Crate but provide a name with the 'put' call.
# here the box will be named cratebox
c.put(Box()), name='cratebox')

# next put a new Box with a name inside a Crate. No other name is given.
# here the box will be named thisbox
c.put(Box(name='thisbox'))

# then we put a new Box with a name inside a Crate but specify a different name for the box
# when the box is created it will be named 'thisbox'
# however when it's input into the crate it will be renamed 'cratebox2'
# moral: if you provide a name with 'put' it overrides any existing item name
c.put(Box(name='thisbox'), name='cratebox2')
```

**Mutables are deepcopied before being added to box** \
**So this won't actually update authors previously stored in the box**
```
authors['Sontag'] = 'On Photography'
```

**Locking the box stops contents from being added or removed**
```
b.lock('secret')            # must provide the key
b.put(song)                 # fails because box has been locked
b.put(song, key='secret')   # add key to open; stays open
b.open('secret')            # alternative: open box and then put new item
```

**Get and set names for items**
```
b.name_contents                 # returns tuples of (name, item)
b.contents                      # returns list of items i.e. the objects
b.names                         # returns list of item names
b.name                          # name of vessel; only works for vessels
b.name = 'new box name'         # set/rename        
b.getname(fibonacci)            # get name of fibonacci item
                                # works for python base objects eg lists, strings etc
b.setname(fibonacci, 'fibo')    # set name for fibonacci item; must be unique
```

**Returns and removes an item from vessel**
```
fetched = b.fetch(name='authors')   # get item named
fetched = b.fetch(index=1)          # get second item in vessel
```

**Return an item from vessel without removing it** \
**nb. changes to item will be reflected in the box**
```
using = b.use(name='myset')     # get item using its name
using = b.use(index=0)          # get item by index
```

**Delete an item from a vessel**
```
b.destroy(name=myset)       # fails because should be string
b.destroy(name='simples')   # destroy by item name
b.destroy(item=sq_primes)   # destroy by variable name
b.destroy(index='1')        # fails because should be integer
b.destroy(index=1)          # destroy by index
```

**Empty vessel contents**
```
b.empty()
```

**Check status - return True or False**
```
b.isopen
b.isempty
b.contains(authors)
```
