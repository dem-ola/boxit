import os, sys, random, math
from copy import deepcopy
from boxit import Vessel, Box, Crate, Container

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
            'Redemption Song',
            set([3,7,9,23,True]),
            authors := {
                'Shakespeare' : 'As You Like It',
                'Hemingway' : 'The Old Man And The Sea',
                'Atwood': "The Handmaid's Tale",
                'Angelou': 'I Know Why The Caged Bird Sings',
            },
            [0,1,1,2,3,5,8,13,21,34],
            ((1,1), (3,9), (5,25), (7,49), (11,121)),
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
def test_find(i, V, method, key, to_test):
    ''' test use, fetch and destroy '''
    func = V.__getattribute__(method)
    kwargs = {key: to_test} # create kwargs to pass to func
    if method == 'use':
        if key == 'index':
            to_test = V.names[to_test]
        assert V.getname(func(**kwargs)) == to_test
    else:
        func(**kwargs)
        assert to_test not in V.names

@yell
def test_lock(i, V, item, lock_meth, key, expect, expect_fail=False):
    V.__getattribute__(lock_meth)(key=key)
    assert V.put(item, key=key) == expect

@yell
def test_mutables(i, V, to_test, expect):
    assert V.use(name=to_test) == expect

@yell
def test_getname(i, V, to_test, expect):
    assert to_test.name == expect

@yell
def test_naming(i, V, action, key, item, name1, expect_fail=False):

    if action == 'get':
        if issubclass(item.__class__, Vessel):
            name = item.name
        else:
            name = V.getname(item)
        assert name == name1

    elif action == 'set':
        if issubclass(item.__class__, Vessel):
            item.name = name1
        else:
            V.setname(item, name1)
        assert name1 in V.names
    
    elif action == 'put':
        init_name, put_name = name1
        the_name = put_name if put_name is not None else init_name
        if isinstance(V, Box):
            V.put(round(math.pi,i),name=the_name) # round so unique
        else:
            V.put(item(key=key,name=init_name), name=put_name)
        assert the_name in V.names


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
    print(V.names)


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
    # note you can't save a Vessel twice as they can't be deepcopied
    # so assigning a diff name does not work - must be a new name
    _ds.p(); _dl.p('duplicate', 0)
    suite = (
         # FAIL - item already exists
        (puts[0], names[0], True),
        # PASS - diff name None & mutables are deepcopied; but FAIL for Boxes
        # Boxes are not deepcopied             
        (puts[1], None, False if v is None else True),
        # PASS - ditto above                     
        (puts[1], 'another ' + names[1], False if v is None else True), 
        # FAIL - tho copy but existing name
        (puts[1] if v is None else v(key='secret'), names[1], True),
        # PASS - for Vessels must be new instance and new name
        ("new thing" if v is None else v(key='secret'), 'new thing', False),
    )
    for s, t in enumerate(suite):
        test_duplicate (s, V, t[0], t[1], expect_fail=t[2])
    print(V.names)


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
        print(V.contents)


    # names - nb. provide key if box is locked
    # tuple of 'name', object type for objs with names 
    _ds.p(); _dl.p('naming', 0)
    key = 'secret'
    # provide a name for item - this will be used
    # but if item already named and another given - new name is used
    suite = (
        ('get', key, V.contents[0], names[0], False), 
        
        # can't set to an existing name except it's None
        ('set', key, V.contents[0], names[1], True),                # FAIL
        ('set', key, V.contents[0], 'reset ' + names[0], False),    # PASS 
        ('set', key, V.contents[1], None, False),                   # PASS

        ('put', key, v, ('aname'+str(v), None), False), 
        ('put', key, v, ('aname2'+str(v), 'bname'+str(v)), False), 
    )
    for s, t in enumerate(suite):
        test_naming (s, V, t[0], t[1], t[2], t[3], expect_fail=t[4] )


    # assign names to items so we can use, fetch, destroy etc by name
    # we need to track where names changed from None
    # b/c renamed items are removed and then re-input renamed at end of list
    # we'll lose our place if merely using a for loop
    k = 0
    for j in range(len(V.contents)):
        name_ = V.getname(V.contents[j-k])
        if name_ == None:
            new_name = 'None'+str(i)+str(k)
            V.setname(V.contents[j-k], new_name)
            k += 1

    finds = ['use', 'fetch', 'destroy']
    for f in finds:
        _ds.p(); _dl.p(f, 0)
        suite = (
            ('name', V.names[0]),
            ('index', 0),
        )
        for s, t in enumerate(suite):
            test_find (s, V, f, t[0], t[1])
   

    # empty box contents - must provide key if box is closed
    _ds.p(); _dl.p('status', 0)
    V.empty()
    print('isopen', V.isopen)
    print('isempty', V.isempty)









