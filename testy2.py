import os, sys, random, math
from copy import deepcopy
from boxit import BoxType, Box, Crate, Container

# place top directory name on sys.path so we can import 
# from sibling packages
dir_ = os.path.dirname(os.path.abspath(__file__)).split('/')
dir_ = '/'.join(dir_[:-1])
sys.path.insert(0, dir_)

# make some print dividers
from yonder.classy.printy import Divider
_de = Divider('=', 40)
_dl = Divider('-', 20)
_ds = Divider('', 20)

# items 
vessels = None, Box, Crate, Container
boxes, crates, containers = [], [], []
item_names = ['foo', 'bar', 'fizz', 'buzz']
box_names = ['bfoo', 'bbar', 'bfizz', 'bbuzz']
crate_names = ['cfoo', 'cbar', 'cfizz', 'cbuzz']
boxitems = [
            myset := set([3,7,9,23,True]),
            fibo :=[0,1,1,2,3,5,8,13,21,34],
            sq_primes := ((1,1), (3,9), (5,25), (7,49), (11,121)),
            authors := {
                'Shakespeare' : 'As You Like It',
                'Hemingway' : 'The Old Man And The Sea',
                'Atwood': "The Handmaid's Tale",
                'Angelou': 'I Know Why The Caged Bird Sings',
            },
            song := 'Redemption Song',
            ]

# -------------------------------------------
# Decorator to print Pass/Fail
# -------------------------------------------
def yell(func):
    ''' print PASS/FAIL '''
    
    def wrap(*args, **kwargs):
        try:
            func(*args, **kwargs)
            print('...')
        except:
            expect_fail = kwargs.get('expect_fail', False)
            if expect_fail == True:
                print('...')
            else:
                print('FAILED: ', func.__code__.co_name, '->', args[0])
    return wrap


# -------------------------------------------
# Assert and print
# -------------------------------------------
@yell
def test_contains(i, V, to_test, expect, expect_fail=False):
    assert V.contains(to_test) == expect

@yell
def test_duplicate(i, V, to_test, name, expect_fail=False):
    failed = False
    try: V.put(to_test, name=name)
    except: failed = True
    assert failed == expect_fail

@yell
def test_using(i, V, key, to_test, expect):
    if key == 'name':       assert V.use(name=to_test) == expect
    elif key == 'index':    assert V.use(index=to_test) == expect

@yell
def test_fetch(i, V, key, to_test, expect):
    if key == 'name':       assert V.fetch(name=to_test) == expect
    elif key == 'index':    assert V.fetch(index=to_test) == expect

@yell
def test_lock(i, V, item, lock_meth, key, expect, expect_fail=False):
    V.__getattribute__(lock_meth)(key=key)
    assert V.put(item, key=key) == expect

@yell
def test_mutables(i, V, to_test, expect):
    assert V.use(name=to_test) == expect

@yell
def test_naming(i, V, v, action, key, name1, name2, expect_fail=False):

    if action == 'get': 
        print(500, V.contents)
        print(V.names)
    
    elif action == 'put':
        print(501, V.contents)
        if isinstance(V, Box):
            V.put(math.pi,name=name1)
            assert name1 in [a[0] for a in V.names]
        else:
            V.put(v(key=key,name=name1), name=name2)
            if name2 is None:
                assert name1 in [a[0] for a in V.names]
            else:
                assert name2 in [a[0] for a in V.names]
    
    elif action == 'set':
        print(502, V.contents)
        if name1 == 'first':
            V.setname(0, name1) # nb fails because has name already
        elif name1 == 'last':
            #print(510, V.names)
            #print(513, V.contents)
            V.setname(len(V.names)-1, name1)
            #print(515,V.names)




# -------------------------------------------
# Run through suite
# -------------------------------------------
for i in range(len(vessels)-1):

    puts = []
    v = vessels[i]
    V = vessels[i+1](key='secret') # empty container for v

    _ds.p()
    _ds.p()
    _de.p(V.__repr__().upper())

    # names for vessel items
    names = item_names
    if v == Box: names = box_names
    elif v == Crate: names = crate_names
    
    rng = 5
    _ds.p(); _dl.p('assign init names', 0)
    for j in range(rng):
        name = names[j] if j < len(names) else None
        if v is None: # items for Box
            item = boxitems[j]
            V.put(item, name=name)
        else: 
            # items for Crates and Containers
            item = v(key='secret')
            V.put(item, name=name)
        puts.append(item)
        print(name,'->',item)


    # show contents
    _ds.p(); _dl.p('contents', 0)
    print(V.contents)


    # if has item
    _ds.p(); _dl.p('contains', 0)
    suite = (
        (authors, True, False if isinstance(V, Box) else True),
        (V.contents[1], True, False),
        (V.names[0], True, False),
    )
    for s, t in enumerate(suite):
        test_contains (s, V, t[0], t[1], expect_fail=t[2])


    # if has item already
    _ds.p(); _dl.p('duplicate', 0)
    if v is None:
        cpy = deepcopy(puts[0])
    suite = (
        (puts[0], names[0], True),              # fail - item already exists
        (puts[0], None, True),                  # ditto despite None name
        (puts[0], 'another ' + names[0], True), # ditto diff name
        (deepcopy(puts[0]) if v is None else v(key='secret'), names[0], True),
        # ditto - tho copy but existing name
        (deepcopy(puts[0]) if v is None else v(key='secret'), 'another ' + names[0], False),
        # pass - uses cpy and new name
        (deepcopy(puts[0]) if v is None else v(key='secret'), None, False),
        # ditto
    )
    for s, t in enumerate(suite):
        test_duplicate (s, V, t[0], t[1], expect_fail=t[2])
        

    # return an item without removing it
    _ds.p(); _dl.p('using', 0)
    res = boxitems[0] if v==None else puts[0]
    suite = (
        ('index', 0, res),
        ('name', names[0], res),
    )
    for s, t in enumerate(suite):
        test_using (s, V, t[0], t[1], t[2])
   

    # return and remove item
    _ds.p(); _dl.p('fetch', 0)
    res = boxitems[0] if v==None else puts[0]
    res1 = boxitems[1] if v==None else puts[1]
    suite = (
        ('index', 0, res),
        ('name', names[1], res1),
    )
    for s, t in enumerate(suite):
        test_fetch (s, V, t[0], t[1], t[2])

    # locks
    _ds.p(); _dl.p('lock', 0)
    right_key = 'secret'; wrong_key = 'boo'
    suite = (
        # stae, key, expect=None as func returns nothing, expected_fail
        ('open', right_key, None, False),
        ('open', None, None, False),
        ('lock', None, None, True),       # should fail - need key
        ('lock', wrong_key, None, True),  # should fail - wrong key
        ('lock', right_key, None, False),
        ('open', None, None, True),       # should fail - need key
        ('open', wrong_key, None, True),  # should fail - wrong key
        ('open', right_key, None, False),  
    )
    for s, t in enumerate(suite):
        # trivial item for Box items to avoid duplicates which is a diff test
        item = str(s*s) if isinstance(V, Box) else vessels[i]()
        test_lock (s, V, item, t[0], t[1], t[2], expect_fail=t[3])    


    # mutables are deepcopied before being added to box
    # so this won't actually update something in the box
    if isinstance(V, Box):
        item = authors
        old = deepcopy(item)                    # keep to compare
        name = names[boxitems.index(item)]      # get item name 
        authors['Sontag'] = 'On Photography'    # update mutable
       
        _ds.p(); _dl.p('mutables', 0)
        print('mutable updated -> ', authors)   # see updated
        suite = (
            (name, old),                        # should remain as old keep
        )
        for s, t in enumerate(suite):
            test_mutables (s, V, t[0], t[1])

    print(V._hash_dict)


    '''

    # names - nb. provide key if box is locked
    # tuple of 'name', object type for objs with names 
    _ds.p(); _dl.p('naming', 0)
    key = 'secret'
    # provide a name for item - this will be used
    # but if item already named and another given - new name is used
    suite = (
        ('get', key, name1:=None, name2:=None), 
        ('put', key, name1:='aname', name2:=None), 
        ('put', key, name1:='bname', name2:='cname'),
        ('set', key, name1:='first', name2:=True),      #overload name2: fail?
        ('set', key, name1:='last', name2:='dname'),
        ('ren', key, name1:='aname', name2:='ename'), 
        ('del', key, name1:='cname', name2:=None),
    )
    for s, t in enumerate(suite):
        print('------')
        print('t3',t[3])
        test_naming (s, V, v, t[0], t[1], t[2], t[3], expect_fail=t[3])


    
        

    # delete an item in the box 
    #V.destroy(name=foo)       # fails because should be string
    #V.destroy(name='simples')   # destroy by item name - doesn't exist
    V.destroy(name=names[0])   # destroy by item name
    #V.destroy(index='1')        # fails because should be integer
    V.destroy(index=1)          # destroy by index

    print(V.names)


    # empty box contents - must provide key if box is closed
    V.empty()
    # check status - these return True or False
    print('isopen', V.isopen)
    print('isempty', V.isempty)

    '''









