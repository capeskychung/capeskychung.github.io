---
layout: article
title: "python winreg模块"
categories: python
#excerpt:
tags: [winreg, python]
image:
#	teaser: /teaser/index.jpeg
date: 2018-03-25T11:04:00+01:00
---

\_winreg用法，python用于操作windows注册表模块.

#### 
#### ismodule
{% highlight python %}
{}
def ismodule(object):
    """Return true if the object is a module.

    Module objects provide these attributes:
        __doc__         documentation string
        __file__        filename (missing for built-in modules)"""
    return isinstance(object, types.ModuleType)
{% endhighlight %}


#### isclass
{% highlight python %}
def isclass(object):
    """Return true if the object is a class.

    Class objects provide these attributes:
        __doc__         documentation string
        __module__      name of module in which this class was defined"""
    return isinstance(object, (type, types.ClassType))
{% endhighlight %}


#### ismethod
用来判断一个方法是否是一个类的成员方法
{% highlight python %}
def ismethod(object):
    """Return true if the object is an instance method.

    Instance method objects provide these attributes:
        __doc__         documentation string
        __name__        name with which this method was defined
        im_class        class object in which this method belongs
        im_func         function object containing implementation of method
        im_self         instance to which this method is bound, or None"""
    return isinstance(object, types.MethodType)
{% endhighlight %}

#### ismethoddescriptor
{% highlight python %}
def ismethoddescriptor(object):
    """Return true if the object is a method descriptor.

    But not if ismethod() or isclass() or isfunction() are true.

    This is new in Python 2.2, and, for example, is true of int.__add__.
    An object passing this test has a __get__ attribute but not a __set__
    attribute, but beyond that the set of attributes varies.  __name__ is
    usually sensible, and __doc__ often is.

    Methods implemented via descriptors that also pass one of the other
    tests return false from the ismethoddescriptor() test, simply because
    the other tests promise more -- you can, e.g., count on having the
    im_func attribute (etc) when an object passes ismethod()."""
    return (hasattr(object, "__get__")
            and not hasattr(object, "__set__") # else it's a data descriptor
            and not ismethod(object)           # mutual exclusion
            and not isfunction(object)
            and not isclass(object))
{% endhighlight %}


#### isdatadescriptor
{% highlight python %}
def isdatadescriptor(object):
    """Return true if the object is a data descriptor.

    Data descriptors have both a __get__ and a __set__ attribute.  Examples are
    properties (defined in Python) and getsets and members (defined in C).
    Typically, data descriptors will also have __name__ and __doc__ attributes
    (properties, getsets, and members have both of these attributes), but this
    is not guaranteed."""
    return (hasattr(object, "__set__") and hasattr(object, "__get__"))
{% endhighlight %}

#### ismemberdescriptor(object)
{% highlight python %}
if hasattr(types, 'MemberDescriptorType'):
    # CPython and equivalent
    def ismemberdescriptor(object):
        """Return true if the object is a member descriptor.

        Member descriptors are specialized descriptors defined in extension
        modules."""
        return isinstance(object, types.MemberDescriptorType)
else:
    # Other implementations
    def ismemberdescriptor(object):
        """Return true if the object is a member descriptor.

        Member descriptors are specialized descriptors defined in extension
        modules."""
        return False
{% endhighlight %}


#### isgetsetdescriptor
{% highlight python %}
if hasattr(types, 'GetSetDescriptorType'):
    # CPython and equivalent
    def isgetsetdescriptor(object):
        """Return true if the object is a getset descriptor.

        getset descriptors are specialized descriptors defined in extension
        modules."""
        return isinstance(object, types.GetSetDescriptorType)
else:
    # Other implementations
    def isgetsetdescriptor(object):
        """Return true if the object is a getset descriptor.

        getset descriptors are specialized descriptors defined in extension
        modules."""
        return False
{% endhighlight %}


#### isfunction
{% highlight python %}
def isfunction(object):
    """Return true if the object is a user-defined function.

    Function objects provide these attributes:
        __doc__         documentation string
        __name__        name with which this function was defined
        func_code       code object containing compiled function bytecode
        func_defaults   tuple of any default values for arguments
        func_doc        (same as __doc__)
        func_globals    global namespace in which this function was defined
        func_name       (same as __name__)"""
    if _signature_is_functionlike(object):
        return True
    return isinstance(object, types.FunctionType)

def _signature_is_functionlike(obj):
    if not callable(obj) or isclass(obj):
        return False
    return type(obj).__name__ == 'cython_function_or_method'
{% endhighlight %}


#### isgeneratorfunction
{% highlight python %}
def isgeneratorfunction(object):
    """Return true if the object is a user-defined generator function.

    Generator function objects provides same attributes as functions.

    See help(isfunction) for attributes listing."""
    return bool((isfunction(object) or ismethod(object)) and
                object.func_code.co_flags & CO_GENERATOR)
{% endhighlight %}


#### istraceback
{% highlight python %}
def istraceback(object):
    """Return true if the object is a traceback.

    Traceback objects provide these attributes:
        tb_frame        frame object at this level
        tb_lasti        index of last attempted instruction in bytecode
        tb_lineno       current line number in Python source code
        tb_next         next inner traceback object (called by this level)"""
    return isinstance(object, types.TracebackType)
{% endhighlight %}



#### isframe
栈帧表示程序运行时函数调用栈中的某一帧。函数没有属性可以获取它，因为它在函数调用时才会产生，而生成器则是由函数调用返回的，所以有属性指向栈帧。获取某个函数的相关的栈帧，则必须在调用这个函数且这个函数尚未放回时获取。通过sys.getframe()函数或者inspect模块的currentframe()函数获取当前栈帧。属性为只读
{% highlight python %}
def isframe(object):
    """Return true if the object is a frame object.

    Frame objects provide these attributes:
        f_back          next outer frame object (this frame's caller) 调用栈的前一帧
        f_builtins      built-in namespace seen by this frame
        f_code          code object being executed in this frame 栈帧对应的code对象
        f_exc_traceback traceback if raised in this frame, or None
        f_exc_type      exception type if raised in this frame, or None
        f_exc_value     exception value if raised in this frame, or None
        f_globals       global namespace seen by this frame
        f_lasti         index of last attempted instruction in bytecode
        f_lineno        current line number in Python source code
        f_locals        local namespace seen by this frame
        f_restricted    0 or 1 if frame is in restricted execution mode
        f_trace         tracing function for this frame, or None"""
    return isinstance(object, types.FrameType)
{% endhighlight %}

{% highlight c %}
// 每个栈用PyFrameObject结构表示
typedef struct _frame {
    PyObject_VAR_HEAD
    struct _frame *f_back;     // 前一个运行栈，调用方
    PyCodeObject *f_code;      // 执行的PyCodeObject对象
    PyObject *f_builtins;      // builtins环境变量集合
    PyObject *f_globals;       // globals全局变量集合
    PyObject *f_locals;        // locals本地变量集合
    PyObject **f_valuestack;   // 栈起始地址，最后一个本地变量之后
    PyObject **f_stacktop;     // 栈针位置，指向栈中下一个空闲位置
    PyObject *f_trace;         // trace函数
    PyObject *f_exc_type, *f_exc_value, *f_exc_traceback;  // 记录异常处理
    PyThreadState *f_tstate;   // 当前的线程
    int f_lasti;		       // 当前执行的字节码的地址
    int f_lineno;		       // 当前的行号
    int f_iblock;		       // 一些局部block块
    PyTryBlock f_blockstack[CO_MAXBLOCKS]; /* for try and loop blocks */
    PyObject *f_localsplus[1];	// 栈地址，大小为 本地变量+co_stacksize
} PyFrameObject;
{% endhighlight %}
![image](https://fanchao01.github.io/blog/images/python_frame_structure.png)
当执行函数调用时会进入新的栈帧，那么当前栈帧就作为下一个栈帧的f_back字段。  
![image](https://fanchao01.github.io/blog/images/python_frame_link.png)
多个栈帧链属于一个线程，而同时可能存在多个线程，每个线程拥有一个栈帧链。这样形成了Python的虚拟机运行环境。  
![image](https://fanchao01.github.io/blog/images/python_runtime_env.png)

参考：https://fanchao01.github.io/blog/2016/11/13/python-pycode_and_frame/

#### iscode
代码块由类源代码、函数源代码或者简单的代码编译。code属性全部是只读的。  
- co_argcount:普通参数的总数，不包括* 参数和 ** 参数  
- co_names:所有的参数名(包括* 参数和 ** 参数)和局部变量名的元组，  
- co_varnames:所有局部变量的元组。   
- co_filename: 源代码所在的文件名。   
- co_flags:一个数值，每一个二进制度包含了特定的信息。 0b100(0x4)和0b1000(0x8)，如果co_flags & 0b100 != 0，说明使用了* args参数；如果co_flags & 0b1000 != 0，说明使用了**kwargs参数。如果co_flags & 0b100000(0x20) != 0，则说明这是一个生成器函数(generator function)
{% highlight python %}
def iscode(object):
    """Return true if the object is a code object.

    Code objects provide these attributes:
        co_argcount     number of arguments (not including * or ** args)
        co_code         string of raw compiled bytecode
        co_consts       tuple of constants used in the bytecode
        co_filename     name of file in which this code object was created
        co_firstlineno  number of first line in Python source code
        co_flags        bitmap: 1=optimized | 2=newlocals | 4=*arg | 8=**arg
        co_lnotab       encoded mapping of line numbers to bytecode indices
        co_name         name with which this code object was defined
        co_names        tuple of names of local variables
        co_nlocals      number of local variables
        co_stacksize    virtual machine stack space required
        co_varnames     tuple of names of arguments and local variables"""
    return isinstance(object, types.CodeType)
{% endhighlight %}

{% highlight c %}
typedef struct {
    PyObject_HEAD
    int co_argcount;        /* 位置参数个数 */
    int co_nlocals;         /* 局部变量个数 */
    int co_stacksize;       /* 栈大小 */
    int co_flags;
    PyObject *co_code;      /* 字节码指令序列 */
    PyObject *co_consts;    /* 所有常量集合 */
    PyObject *co_names;     /* 所有符号名称集合 */
    PyObject *co_varnames;  /* 局部变量名称集合 */
    PyObject *co_freevars;  /* 闭包用的的变量名集合 */
    PyObject *co_cellvars;  /* 内部嵌套函数引用的变量名集合 */

    /* The rest doesn’t count for hash/cmp */
    PyObject *co_filename;  /* 代码所在文件名 */
    PyObject *co_name;      /* 模块名|函数名|类名 */
    int co_firstlineno;     /* 代码块在文件中的起始行号 */
    PyObject *co_lnotab;    /* 字节码指令和行号的对应关系 */
    void *co_zombieframe;   /* for optimization only (see frameobject.c) */
} PyCodeObject;
{% endhighlight %}

加载模块时，模块对应的PyCodeObject对象被写入.pyc文件，格式：  


block | type | description
---| ---|--- 
MAGIC | long | 魔数，区分不同版本的python  
MTIME |	long | 修改时间  
TYPE_CODE |	byte | PyCodeObject对象  
co_argcount | long | 对应PyCodeObject结构体各个域     
co_nlocals | long |  	
co_stacksize | long |  	
co_flags | long |  	
TYPE_STRING | byte | "字符串表示方法，对应PyCodeObject中的co_code"
co_code size | long	
co_code value | bytes	
TYPE_LIST | byte | 列表
co_const size | long | 列表co_consts的元素个数
TYPE_INT | byte	| co_const[0]是一个整型
co_const[0]	| long	
TYPE_STRING	| byte | co_consts[1]是一个字符串
co_consts[1] size	| long	
co_consts[1] value	| bytes	
TYPE_CODE | byte | co_consts[2]是一个PyCodeObject对象，对应的代码可能是一个函数或者类
co_consts[2] | 	


co_flags
{% highlight c %}
#define CO_OPTIMIZED	0x0001
#define CO_NEWLOCALS	0x0002
#define CO_VARARGS	0x0004
#define CO_VARKEYWORDS	0x0008
#define CO_NESTED       0x0010
#define CO_GENERATOR    0x0020
/* The CO_NOFREE flag is set if there are no free or cell variables.
   This information is redundant, but it allows a single flag test
   to determine whether there is any extra work to be done when the
   call frame it setup.
*/
#define CO_NOFREE       0x0040

#if 0
/* This is no longer used.  Stopped defining in 2.5, do not re-use. */
#define CO_GENERATOR_ALLOWED    0x1000
#endif
#define CO_FUTURE_DIVISION    	0x2000
#define CO_FUTURE_ABSOLUTE_IMPORT 0x4000 /* do absolute imports by default */
#define CO_FUTURE_WITH_STATEMENT  0x8000
#define CO_FUTURE_PRINT_FUNCTION  0x10000
#define CO_FUTURE_UNICODE_LITERALS 0x20000

/* This should be defined if a future statement modifies the syntax.
   For example, when a keyword is added.
*/
#if 1
#define PY_PARSER_REQUIRES_FUTURE_KEYWORD
#endif
{% endhighlight %}

{% highlight python %}
def f(x, y = 10, z = 16):
    print z
{% endhighlight %}
dir(f) ---> ['func_closure', 'func_code', 'func_defaults', 'func_dict', 'func_doc', 'func_globals', 'func_name']
在funcobject.c中对PyFunction_Type的定义：
{% highlight c %}
static PyMemberDef func_memberlist[] = {
    {"func_closure", T_OBJECT, OFF(func_closure), RESTRICTED|READONLY},
    {"func_doc",     T_OBJECT, OFF(func_doc), WRITE_RESTRICTED},
    {"__doc__",      T_OBJECT, OFF(func_doc), WRITE_RESTRICTED},
    {"func_globals", T_OBJECT, OFF(func_globals), RESTRICTED|READONLY},
    {"__module__",   T_OBJECT, OFF(func_module), WRITE_RESTRICTED},
    {NULL}  /* Sentinel */
};

static PyGetSetDef func_getsetlist[] = {
    {"func_code", (getter)func_get_code, (setter)func_set_code},
    {"func_defaults", (getter)func_get_defaults, (setter)func_set_defaults},
    {"func_dict", (getter)func_get_dict, (setter)func_set_dict},
    {"__dict__", (getter)func_get_dict, (setter)func_set_dict},
    {"func_name", (getter)func_get_name, (setter)func_set_name},
    {"__name__", (getter)func_get_name, (setter)func_set_name},
    {NULL} /* Sentinel */
};
{% endhighlight %}
f.func_defaults记录的是函数的默认值，tuple(10, 16)

f.func_code是一个code对象，对应PyCodeObject,有三个co_varnames, co_freevars, co_cellvars,分别对应了 local variables, free variables, cell variables.free variables指enclosing scope中的变量，cell variables则是指会被多个scope访问的变量。
{% highlight python %}
def foo():
    a = 5
    def bar():
        return a
    print "cellvars:", bar.func_code.co_cellvars
    print "freevars:", bar.func_code.co_freevars
    return bar

g = foo()
print foo.func_code.co_freevars
print foo.func_code.co_cellvars
{% endhighlight %}

LOAD_GLOBAL在代码对象的co_names属性中寻找变量名。  
LOAD_FAST和STORE_FAST在代码对象的co_varnames属性中寻找变量名。  
注意这些命令的参数都为整数，变量名是通过将参数作为下标从对应的变量名元组中获得的。所以：“LOAD_GLOBAL 0”相当于载入f1.func_globals[f1.func_code.co_names[0]]对象。对于局域变量，Python做了尽可能的优化处理，因此它使用LOAD_FAST和STORE_FAST对局域变量进行存取，它们可以通过其参数直接存取一个用来保存局域变量的C语言数组。    

#### isbuiltin
{% highlight python %}
def isbuiltin(object):
    """Return true if the object is a built-in function or method.

    Built-in functions and methods provide these attributes:
        __doc__         documentation string
        __name__        original name of this function or method
        __self__        instance to which a method is bound, or None"""
    return isinstance(object, types.BuiltinFunctionType)
{% endhighlight %}


#### isroutine
{% highlight python %}
def isroutine(object):
    """Return true if the object is any kind of function or method."""
    return (isbuiltin(object)
            or isfunction(object)
            or ismethod(object)
            or ismethoddescriptor(object))
{% endhighlight %}

#### isabstract
{% highlight python %}
def isabstract(object):
    """Return true if the object is an abstract base class (ABC)."""
    return bool(isinstance(object, type) and object.__flags__ & TPFLAGS_IS_ABSTRACT)
{% endhighlight %}


#### getmembers
{% highlight python %}
def getmembers(object, predicate=None):
    """Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only return members that satisfy a given predicate."""
    results = []
    for key in dir(object):
        try:
            value = getattr(object, key)
        except AttributeError:
            continue
        if not predicate or predicate(value):
            results.append((key, value))
    results.sort()
    return results
{% endhighlight %}



#### getmro
{% highlight python %}
def getmro(cls):
    "Return tuple of base classes (including cls) in method resolution order."
    if hasattr(cls, "__mro__"):
        return cls.__mro__
    else:
        result = []
        _searchbases(cls, result)
        return tuple(result)
{% endhighlight %}
