

def run(f):
    next(f)
    return f
'''
def merge_result(res_arr):
    ok=[x[1] for x in res_arr if x[0]=='ok']
    if len(ok)!=0 :
        return ('ok',ok)
    running=[x[1] for x in res_arr if x[0]=='running']
    if len(running)!=0 :
        return ('running',running)
    return ('fail',res_arr)
'''   
def pstr(s):
    for x in s:
       ch=yield('running',' cmp',s,x)
       if ch!=x :
           while True : yield('fail',('pstr',s,"where %s!=%s"%(ch,x)))
    yield('ok',('str',s))
    while True : yield('fail',('pstr',s,'is done.'))

def pboolean(ga,gb,func_oa_ob):
    a=ga()
    b=gb()
    oa=next(ga)
    ob=next(gb)
    while True:
        ret= func(oa,ob)
        if ret[0]=='fail':
            while True: yield ret 
        ch=yield ret
        oa=a.send(ch)
        ob=b.send(ch)

def pbor(oa,ob):
    if oa[0]=='ok' :
        return ('ok',('or',oa[1]))
    elif ob[0]=='ok' :
        return ('ok',('or',ob[1]))
    elif oa[0]=='running' and ob[0]=='running':
        return ('running',('or',oa[1],ob[1]))
    else:
        return ('fail',('or',oa[1],ob[1]))

def pband(oa,ob):
    if oa[0]=='ok' and  ob[0]=='ok' :
        return ('ok',('and',oa[1],ob[1]))
    elif oa[0]=='ok' and ob[0]=='running':
        return ('running',('and',ob[1]))
    elif oa[0]=='running' and ob[0]=='ok':
        return ('running',('and',oa[1]))
    else:
        return ('fail',('and',oa[1],ob[1]))
    

def plink(ga,gb):
    bpool=[]# b,prefix
    ret=None
    a=ga()
    oa=next(a)
    if oa[0]=='ok' :
        b=gb()
        bpool.append((b,[]))
        ob=next(b)
        ret= (ob[0],('link',[((),ob[1]),]))
    else:
        ret= ('running',('link','start'))

    while True:
        if oa[0]=='fail' and len(bpool)==0 :
            while True : yield ('fail',('link',oa[1]))
        ch=yield ret
        tempbpool=[]
        retarr=[]
        for bi in bpool:
            ob=bi[0].send(ch)
            if ob[0]!='fail' :
                tempbpool.append(bi)
                retarr.append((ob[0],bi[1],ob[1]))# (state, prefix, res)
        bpool=tempbpool
        if a!=None :
            oa=a.send(ch)
            if oa[0]=='ok' :
                b=gb()
                bpool.append((b,oa[1]))
                ob=next(b)
                retarr.append((ob[0],oa[1],ob))
        okbi=[x for x in retarr if x[0]=='ok']
        if len(okbi)!=0 :
            print('link--',okbi)
            ret=('ok',('link',[(x[1],x[2]) for x in okbi]))
        else:
            ret=('running',('link',[(x[1],x[2]) for x in retarr if x[0]!='fail']))


def pmulti(ga,beg=0,end=999):
    ret=('running',('multi','start'))
    if beg<=0 : ret=('ok',('multi',[]))
    tasks=[]#(iternum,genf,prefix)
    a=ga()
    next(a)
    tasks.append((1,a,[]))
    #ignore 0size a
    while len(tasks)!=0 :
        ch=yield ret#('ok',('multi',[(num,res), ...]))
        okarr=[]#(num,res)
        ttasks=[]
        for ti in tasks:
            if ti[0]>=end : continue
            ot=ti[1].send(ch)
            if ot[0]=='running':
                ttasks.append(ti)
            elif ot[0]=='ok':
                ttasks.append(ti)
                if ti[0]>=beg: okarr.append(ti[2]+[ot[1],])
                a=ga()
                next(a)#ignore 0size a
                ttasks.append((ti[0]+1, a, ti[2]+[ot[1],]))
        print('tasks',tasks,a)
        tasks=ttasks
        if len(okarr)!=0:
            ret=('ok',('multi',okarr))
        else:
            ret=('running',('multi',tasks))
    while True: yield ('fail',('multi','no match'))

'''
def por(ga,gb):
    a=run(ga())
    b=run(gb())
    ch=yield('running','or start')
    while True:
        oa=a.send(ch)
        ob=b.send(ch)
        ret=[]
        ok0=[x[1] for x in oa if x[0]=='ok']
        ok1=[x[1] for x in ob if x[0]=='ok']
        if len(ok0)!=0 :
            ret.append(('ok',('or0',ok0)))
        if len(ok1)!=0 :
            ret.append(('ok',('or1',ok1)))

        run01=[x for x in oa if x[0]=='running']+[x[1] for x in ob if x[0]=='running']
        if len(run01)!=0 :
            ret.append(('running',run01))
        ch=yield ret

def pand(ga,gb):
    a=run(ga())
    b=run(gb())
    ch=yield('running','and start')
    while True:
        oa=a.send(ch)
        ob=b.send(ch)
        ret=[]
        ok0=[x[1] for x in oa if x[0]=='ok']
        ok1=[x[1] for x in ob if x[0]=='ok']
        if len(ok0)!=0 and len(ok1)!=0 :
            ret.append(('ok',('and',ok0+ok1)))

        run01=[x for x in oa if x[0]=='running']+[x for x in ob if x[0]=='running']
        if len(run01)!=0 :
            ret.append(('running',run01))

        ch=yield ret

#    a=run(ga())
#    b=run(gb())
#    ch=yield('running',)
#    while True:
#        oa=a.send(ch)
#        ob=b.send(ch)
#        if oa[0]=='ok' and ob[0]=='ok' :
#            ch=yield('ok',('and',oa[1],ob[1]))
#        elif oa[0]=='fail' or ob[0]=='fail':
#            while True : yield('fail',oa,ob)
#        elif oa[0]=='running' or ob[0]=='running':
#            ch=yield('running',)
#        else :
#            while True : yield('fail','unknow',oa,ob)

def plink(ga,gb):
    aalive=True
    ret=[]
    bpool=[]
    a=ga()
    oa=next(a)
    ok0=[x[1] for x in oa if x[0]=='ok']
    if len(ok0)!=0 :
        b=gb()
        ob=next(b)
        bpool.append((b,[]))
        ok1=[x[1] for x in ob if x[0]=='ok']
        if len(ok1)!=0 :
            ret.append('ok',('link',ok1))
    ret.append([('running',)])
    print('link d3',ret)
    ch= yield ret
    while True:
        ret=[]
        temppool=bpool
        bpool=[]
        print('multi d2 len:',len(temppool))
        for bi in temppool :
            ob=bi[0].send(ch)
            ok1=[x[1] for x in ob if x[0]=='ok']
            if len(ok1)!=0 :
                ret.append(('ok',('link',bi[1],ok1)))
            if len([x for x in ob if x[0]=='running' or x[0]=='ok'])!=0 :
                bpool.append(bi)
                ret.append(('running',))
        if aalive :
            oa=a.send(ch)
            ok0=[x[1] for x in oa if x[0]=='ok']
            if len(ok0)!=0:
                b=gb()
                ob=next(b)
                bpool.append((b,ok0))
                ok1=[x[1] for x in ob if x[0]=='ok']
                if len(ok1)!=0 :
                    ret.append(('ok',('link',ok1)))
            run0=[x for x in oa if x[0]=='running' or x[0]=='ok']
            print('link d1', oa,' *bpool*:', [x[1] for x in bpool])
            if len(run0)==0 :
                print('link d3',oa)
                aalive=False
        if len(ret)==0:
            while True : yield [('fail','end multi')]
        print('link d4',ret)
        ch=yield ret
            
def ponce(ga):
    a=ga()
    oa=next(a)
    while True:
        ok0=[x[1] for x in oa if x[0]=='ok']
        if len(ok0)!=0: 
            yield [('ok',ok0)]
        run0=[x for x in oa if x[0]=='running']
        if len(run0)!=0:
            ch=yield[('running',run0)]
            oa=a.send(ch)
        else:
            while True:
                yield[('fail','ponce')]
        
def pmulti(ga,beg=0,end=999):
    ret=[]
    for i in range(beg):
        a=ga()
        oa=next(a)
        ok0=[x[1] for x in oa if x[0]=='ok']
        if len(ok0)!=0: 
            ret.append(ok0)
            continue
        while True:
            ch=yield [('running',)]
            oa=a.send(ch)
            ok0=[x[1] for x in oa if x[0]=='ok']
            if len(ok0)!=0: 
                ret.append(ok0)
                break
            print('multi d1',oa)
            if len([x for x in oa if x[0]=='running' or x[0]=='ok'])==0:
                while True: yield [('fail','multi1')]

    for i in range(beg,end):
        a=ga()
        oa=next(a)
        ok0=[x[1] for x in oa if x[0]=='ok']
        if len(ok0)!=0: 
            ret.append(ok0)
            continue
        while True:
            ch=yield [('running',),('ok',('multi',i,ret))]
            oa=a.send(ch)
            ok0=[x[1] for x in oa if x[0]=='ok']
            if len(ok0)!=0: 
                ret.append(ok0)
                break
            print('multi d1',oa)
            if len([x for x in oa if x[0]=='running' or x[0]=='ok'])==0:
                print('multi d1.',oa)
                while True: yield [('fail','multi2')]
        
'''


def num_dec():
    ch=yield('running','num start')
    if (ch>='0' and ch<='9'):
        yield('ok',ch)
    while True :yield('fail','num dec')

def m_num():
    return pmulti(lambda:num_dec(),1,10)

def m_muler():
    return plink(lambda:pmulti(lambda:plink(m_num,lambda:pstr('*'))),m_num)
def m_adder():
    return plink(m_muler, lambda:pmulti(lambda:plink(lambda:pstr('+'),m_muler)))


if __name__=='__main__':
    f=run(m_adder())
    r=None
    for ch in '54+3*21':
        r=f.send(ch)
        print(ch,r)
        
    print('--------')
    print(r)
