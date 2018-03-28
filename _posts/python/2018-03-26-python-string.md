---
layout: article
title: "python string模块"
categories: python
#excerpt:
tags: [string, python]
image:
    teaser: /teaser/reg.jpg
date: 2018-03-26T10:04:00+01:00
---

string模块用法.

#### string.capitalize()
将字符串的第一个字符大写      
{% highlight c %}
static PyObject *
string_capitalize(PyStringObject *self)
{
    char *s = PyString_AS_STRING(self), *s_new;
    Py_ssize_t i, n = PyString_GET_SIZE(self);
    PyObject *newobj;

    newobj = PyString_FromStringAndSize(NULL, n);
    if (newobj == NULL)
        return NULL;
    s_new = PyString_AsString(newobj);
    if (0 < n) {
        int c = Py_CHARMASK(*s++);
        if (islower(c))
            *s_new = toupper(c);
        else
            *s_new = c;
        s_new++;
    }
    for (i = 1; i < n; i++) {
        int c = Py_CHARMASK(*s++);
        if (isupper(c))
            *s_new = tolower(c);
        else
            *s_new = c;
        s_new++;
    }
    return newobj;
}
{% endhighlight %}


#### string.center(width)
返回原字符串居中，并使用空格填充长度为width的新字符串
{% highlight c %}
static PyObject *
string_center(PyStringObject *self, PyObject *args)
{
    Py_ssize_t marg, left;
    Py_ssize_t width;
    char fillchar = ' ';

    if (!PyArg_ParseTuple(args, "n|c:center", &width, &fillchar))
        return NULL;

    if (PyString_GET_SIZE(self) >= width && PyString_CheckExact(self)) {
        Py_INCREF(self);
        return (PyObject*) self;
    }

    marg = width - PyString_GET_SIZE(self);
    left = marg / 2 + (marg & width & 1);  // 只有当原先字符串长度为偶数，width为奇数的时候，左边空格长度会加1

    return pad(self, left, marg - left, fillchar);
}
{% endhighlight %}


#### string.count(str, beg=0, end=len(string))
返回str在string里面出现的次数，如果指定beg和end则返回范围内str出现的次数
{% highlight c %}
static PyObject *
string_count(PyStringObject *self, PyObject *args)
{
    PyObject *sub_obj;
    const char *str = PyString_AS_STRING(self), *sub;
    Py_ssize_t sub_len;
    Py_ssize_t start = 0, end = PY_SSIZE_T_MAX;

    if (!stringlib_parse_args_finds("count", args, &sub_obj, &start, &end))
        return NULL;

    if (PyString_Check(sub_obj)) {
        sub = PyString_AS_STRING(sub_obj);
        sub_len = PyString_GET_SIZE(sub_obj);
    }
#ifdef Py_USING_UNICODE
    else if (PyUnicode_Check(sub_obj)) {
        Py_ssize_t count;
        count = PyUnicode_Count((PyObject *)self, sub_obj, start, end);
        if (count == -1)
            return NULL;
        else
            return PyInt_FromSsize_t(count);
    }
#endif
    else if (PyObject_AsCharBuffer(sub_obj, &sub, &sub_len))
        return NULL;

    ADJUST_INDICES(start, end, PyString_GET_SIZE(self));

    return PyInt_FromSsize_t(
        stringlib_count(str + start, end - start, sub, sub_len, PY_SSIZE_T_MAX)
        );
}
{% endhighlight %}

#### string.decode(encoding='UTF-8', errors='strict')
以encoding指定的编码格式解码string，如果出错默认报一个ValueError的异常，除非errors指定的诗ignore或者replace

{% highlight c %}
static PyObject *
string_decode(PyStringObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"encoding", "errors", 0};
    char *encoding = NULL;
    char *errors = NULL;
    PyObject *v;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|ss:decode",
                                     kwlist, &encoding, &errors))
        return NULL;
    v = PyString_AsDecodedObject((PyObject *)self, encoding, errors);
    if (v == NULL)
        goto onError;
    if (!PyString_Check(v) && !PyUnicode_Check(v)) {
        PyErr_Format(PyExc_TypeError,
                     "decoder did not return a string/unicode object "
                     "(type=%.400s)",
                     Py_TYPE(v)->tp_name);
        Py_DECREF(v);
        return NULL;
    }
    return v;

 onError:
    return NULL;
}
{% endhighlight %}


#### string.encode(encoding='UTF-8', errors='strict')
以encoding指定的编码格式编码string，如果出错默认报一个ValueError的异常，除非errors指定的是ignore或者replace  
{% highlight c %}
static PyObject *
string_encode(PyStringObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"encoding", "errors", 0};
    char *encoding = NULL;
    char *errors = NULL;
    PyObject *v;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|ss:encode",
                                     kwlist, &encoding, &errors))
        return NULL;
    v = PyString_AsEncodedObject((PyObject *)self, encoding, errors);
    if (v == NULL)
        goto onError;
    if (!PyString_Check(v) && !PyUnicode_Check(v)) {
        PyErr_Format(PyExc_TypeError,
                     "encoder did not return a string/unicode object "
                     "(type=%.400s)",
                     Py_TYPE(v)->tp_name);
        Py_DECREF(v);
        return NULL;
    }
    return v;

 onError:
    return NULL;
}
{% endhighlight %}

#### string.endswith(obj, beg=0, end=len(string))
检查字符串是否以obj结束，如果beg或者end指定则检查指定范围内是否以obj结束，如果是返回True，否则返回False
{% highlight c %}
static PyObject *
string_endswith(PyStringObject *self, PyObject *args)
{
    Py_ssize_t start = 0;
    Py_ssize_t end = PY_SSIZE_T_MAX;
    PyObject *subobj;
    int result;

    if (!stringlib_parse_args_finds("endswith", args, &subobj, &start, &end))
        return NULL;
    if (PyTuple_Check(subobj)) {
        Py_ssize_t i;
        for (i = 0; i < PyTuple_GET_SIZE(subobj); i++) {
            result = _string_tailmatch(self,
                            PyTuple_GET_ITEM(subobj, i),
                            start, end, +1);
            if (result == -1)
                return NULL;
            else if (result) {
                Py_RETURN_TRUE;
            }
        }
        Py_RETURN_FALSE;
    }
    result = _string_tailmatch(self, subobj, start, end, +1);
    if (result == -1) {
        if (PyErr_ExceptionMatches(PyExc_TypeError))
            PyErr_Format(PyExc_TypeError, "endswith first arg must be str, "
                         "unicode, or tuple, not %s", Py_TYPE(subobj)->tp_name);
        return NULL;
    }
    else
        return PyBool_FromLong(result);
}
{% endhighlight %}

#### string.expandtabs(tabsize=8)
把字符串中的tab符号转为空格，tab符号默认的空格数为8.
{% highlight c %}
static PyObject*
string_expandtabs(PyStringObject *self, PyObject *args)
{
    const char *e, *p, *qe;
    char *q;
    Py_ssize_t i, j, incr;
    PyObject *u;
    int tabsize = 8;

    if (!PyArg_ParseTuple(args, "|i:expandtabs", &tabsize))
        return NULL;

    /* First pass: determine size of output string */
    i = 0; /* chars up to and including most recent \n or \r */
    j = 0; /* chars since most recent \n or \r (use in tab calculations) */
    e = PyString_AS_STRING(self) + PyString_GET_SIZE(self); /* end of input */
    for (p = PyString_AS_STRING(self); p < e; p++) {
        if (*p == '\t') {
            if (tabsize > 0) {
                incr = tabsize - (j % tabsize);
                if (j > PY_SSIZE_T_MAX - incr)
                    goto overflow1;
                j += incr;
            }
        }
        else {
            if (j > PY_SSIZE_T_MAX - 1)
                goto overflow1;
            j++;
            if (*p == '\n' || *p == '\r') {
                if (i > PY_SSIZE_T_MAX - j)
                    goto overflow1;
                i += j;
                j = 0;
            }
        }
    }

    if (i > PY_SSIZE_T_MAX - j)
        goto overflow1;

    /* Second pass: create output string and fill it */
    u = PyString_FromStringAndSize(NULL, i + j);
    if (!u)
        return NULL;

    j = 0; /* same as in first pass */
    q = PyString_AS_STRING(u); /* next output char */
    qe = PyString_AS_STRING(u) + PyString_GET_SIZE(u); /* end of output */

    for (p = PyString_AS_STRING(self); p < e; p++) {
        if (*p == '\t') {
            if (tabsize > 0) {
                i = tabsize - (j % tabsize);
                j += i;
                while (i--) {
                    if (q >= qe)
                        goto overflow2;
                    *q++ = ' ';
                }
            }
        }
        else {
            if (q >= qe)
                goto overflow2;
            *q++ = *p;
            j++;
            if (*p == '\n' || *p == '\r')
                j = 0;
        }
    }

    return u;

  overflow2:
    Py_DECREF(u);
  overflow1:
    PyErr_SetString(PyExc_OverflowError, "new string is too long");
    return NULL;
}
{% endhighlight %}


#### string.find(str, beg=0,end=len(string))
检测str是够包含在string中，如果beg和end指定范围，则检查是否包含在指定范围内，如果是返回开始的索引值，否则返回-1   
{% highlight c %}
static PyObject *
string_find(PyStringObject *self, PyObject *args)
{
    Py_ssize_t result = string_find_internal(self, args, +1);
    if (result == -2)
        return NULL;
    return PyInt_FromSsize_t(result);
}

string_find_internal(PyStringObject *self, PyObject *args, int dir)
{
    PyObject *subobj;
    const char *sub;
    Py_ssize_t sub_len;
    Py_ssize_t start=0, end=PY_SSIZE_T_MAX;

    if (!stringlib_parse_args_finds("find/rfind/index/rindex",
                                    args, &subobj, &start, &end))
        return -2;

    if (PyString_Check(subobj)) {
        sub = PyString_AS_STRING(subobj);
        sub_len = PyString_GET_SIZE(subobj);
    }
#ifdef Py_USING_UNICODE
    else if (PyUnicode_Check(subobj))
        return PyUnicode_Find(
            (PyObject *)self, subobj, start, end, dir);
#endif
    else if (PyObject_AsCharBuffer(subobj, &sub, &sub_len))
        /* XXX - the "expected a character buffer object" is pretty
           confusing for a non-expert.  remap to something else ? */
        return -2;

    if (dir > 0)
        return stringlib_find_slice(
            PyString_AS_STRING(self), PyString_GET_SIZE(self),
            sub, sub_len, start, end);
    else
        return stringlib_rfind_slice(
            PyString_AS_STRING(self), PyString_GET_SIZE(self),
            sub, sub_len, start, end);
}
{% endhighlight %}


#### string.index(str, beg=0, end=len(string))
跟find()方法一样，如果str不在string中会报一个异常    
{% highlight c %}
static PyObject *
string_index(PyStringObject *self, PyObject *args)
{
    Py_ssize_t result = string_find_internal(self, args, +1);
    if (result == -2)
        return NULL;
    if (result == -1) {
        PyErr_SetString(PyExc_ValueError,
                        "substring not found");
        return NULL;
    }
    return PyInt_FromSsize_t(result);
}
{% endhighlight %}


#### string.isalnum
如果string至少有一个字符并且所有的字符都是字母或者数字则返回True，否则返回False      

{% highlight c %}
static PyObject*
string_isalnum(PyStringObject *self)
{
    register const unsigned char *p
        = (unsigned char *) PyString_AS_STRING(self);
    register const unsigned char *e;

    /* Shortcut for single character strings */
    if (PyString_GET_SIZE(self) == 1 &&
        isalnum(*p))
        return PyBool_FromLong(1);

    /* Special case for empty strings */
    if (PyString_GET_SIZE(self) == 0)
        return PyBool_FromLong(0);

    e = p + PyString_GET_SIZE(self);
    for (; p < e; p++) {
        if (!isalnum(*p))
            return PyBool_FromLong(0);
    }
    return PyBool_FromLong(1);
}
{% endhighlight %}

#### string.isalpha
如果string至少有一个字符并且所有字符都是字母则返回True，否则返回False   
{% highlight c %}
static PyObject*
string_isalpha(PyStringObject *self)
{
    register const unsigned char *p
        = (unsigned char *) PyString_AS_STRING(self);
    register const unsigned char *e;

    /* Shortcut for single character strings */
    if (PyString_GET_SIZE(self) == 1 &&
        isalpha(*p))
        return PyBool_FromLong(1);

    /* Special case for empty strings */
    if (PyString_GET_SIZE(self) == 0)
        return PyBool_FromLong(0);

    e = p + PyString_GET_SIZE(self);
    for (; p < e; p++) {
        if (!isalpha(*p))
            return PyBool_FromLong(0);
    }
    return PyBool_FromLong(1);
}
}
{% endhighlight %}


#### string.isdigit   
如果string只包含数字则返回True否则返回False   
{% highlight c %}
static PyObject*
string_isdigit(PyStringObject *self)
{
    register const unsigned char *p
        = (unsigned char *) PyString_AS_STRING(self);
    register const unsigned char *e;

    /* Shortcut for single character strings */
    if (PyString_GET_SIZE(self) == 1 &&
        isdigit(*p))
        return PyBool_FromLong(1);

    /* Special case for empty strings */
    if (PyString_GET_SIZE(self) == 0)
        return PyBool_FromLong(0);

    e = p + PyString_GET_SIZE(self);
    for (; p < e; p++) {
        if (!isdigit(*p))
            return PyBool_FromLong(0);
    }
    return PyBool_FromLong(1);
}
{% endhighlight %}


#### string.islower
如果string中包含至少一个区分大小写的字符，并且所有这些去跟大小写的字符都是小写则返回True，否则返回False
{% highlight c %}
static PyObject*
string_islower(PyStringObject *self)
{
    register const unsigned char *p
        = (unsigned char *) PyString_AS_STRING(self);
    register const unsigned char *e;
    int cased;

    /* Shortcut for single character strings */
    if (PyString_GET_SIZE(self) == 1)
        return PyBool_FromLong(islower(*p) != 0);

    /* Special case for empty strings */
    if (PyString_GET_SIZE(self) == 0)
        return PyBool_FromLong(0);

    e = p + PyString_GET_SIZE(self);
    cased = 0;
    for (; p < e; p++) {
        if (isupper(*p))
            return PyBool_FromLong(0);
        else if (!cased && islower(*p))
            cased = 1;
    }
    return PyBool_FromLong(cased);
}
{% endhighlight %}


#### string.isspace
如果string中只包含空格，则返回True，否则返回False
{% highlight c %}
static PyObject*
string_isspace(PyStringObject *self)
{
    register const unsigned char *p
        = (unsigned char *) PyString_AS_STRING(self);
    register const unsigned char *e;

    /* Shortcut for single character strings */
    if (PyString_GET_SIZE(self) == 1 &&
        isspace(*p))
        return PyBool_FromLong(1);

    /* Special case for empty strings */
    if (PyString_GET_SIZE(self) == 0)
        return PyBool_FromLong(0);

    e = p + PyString_GET_SIZE(self);
    for (; p < e; p++) {
        if (!isspace(*p))
            return PyBool_FromLong(0);
    }
    return PyBool_FromLong(1);
}
{% endhighlight %}


#### string.istitle
如果string是标题化的(见title()),则返回True，否则返回False

{% highlight c %}
static PyObject*
string_istitle(PyStringObject *self, PyObject *uncased)
{
    register const unsigned char *p
        = (unsigned char *) PyString_AS_STRING(self);
    register const unsigned char *e;
    int cased, previous_is_cased;

    /* Shortcut for single character strings */
    if (PyString_GET_SIZE(self) == 1)
        return PyBool_FromLong(isupper(*p) != 0);

    /* Special case for empty strings */
    if (PyString_GET_SIZE(self) == 0)
        return PyBool_FromLong(0);

    e = p + PyString_GET_SIZE(self);
    cased = 0;
    previous_is_cased = 0;
    for (; p < e; p++) {
        register const unsigned char ch = *p;

        if (isupper(ch)) {
            if (previous_is_cased)
                return PyBool_FromLong(0);
            previous_is_cased = 1;
            cased = 1;
        }
        else if (islower(ch)) {
            if (!previous_is_cased)
                return PyBool_FromLong(0);
            previous_is_cased = 1;
            cased = 1;
        }
        else
            previous_is_cased = 0;
    }
    return PyBool_FromLong(cased);
}
{% endhighlight %}


#### string.isupper
如果string中包含至少一个大写的字符并且所有这些（区分大小的）字符都是大写，则返回True，否则返回False
{% highlight c %}
}
static PyObject*
string_isupper(PyStringObject *self)
{
    register const unsigned char *p
        = (unsigned char *) PyString_AS_STRING(self);
    register const unsigned char *e;
    int cased;

    /* Shortcut for single character strings */
    if (PyString_GET_SIZE(self) == 1)
        return PyBool_FromLong(isupper(*p) != 0);

    /* Special case for empty strings */
    if (PyString_GET_SIZE(self) == 0)
        return PyBool_FromLong(0);

    e = p + PyString_GET_SIZE(self);
    cased = 0;
    for (; p < e; p++) {
        if (islower(*p))
            return PyBool_FromLong(0);
        else if (!cased && isupper(*p))
            cased = 1;
    }
    return PyBool_FromLong(cased);
}
{% endhighlight %}


#### string.ljust(width)
返回一个原字符串左对齐，并使用空格填充至长度width的新字符串
{% highlight c %}
static PyObject *
string_ljust(PyStringObject *self, PyObject *args)
{
    Py_ssize_t width;
    char fillchar = ' ';

    if (!PyArg_ParseTuple(args, "n|c:ljust", &width, &fillchar))
        return NULL;

    if (PyString_GET_SIZE(self) >= width && PyString_CheckExact(self)) {
        Py_INCREF(self);
        return (PyObject*) self;
    }

    return pad(self, 0, width - PyString_GET_SIZE(self), fillchar);
}
{% endhighlight %}


#### string.lower
将string中的所有大写字符转成小写
{% highlight c %}
static PyObject *
string_lower(PyStringObject *self)
{
    char *s;
    Py_ssize_t i, n = PyString_GET_SIZE(self);
    PyObject *newobj;

    newobj = PyString_FromStringAndSize(NULL, n);
    if (!newobj)
        return NULL;

    s = PyString_AS_STRING(newobj);

    Py_MEMCPY(s, PyString_AS_STRING(self), n);

    for (i = 0; i < n; i++) {
        int c = Py_CHARMASK(s[i]);
        if (isupper(c))
            s[i] = _tolower(c);
    }

    return newobj;
}
{% endhighlight %}


#### string.lstrip
截掉string左边的空格
{% highlight c %}
static PyObject *
string_lstrip(PyStringObject *self, PyObject *args)
{
    if (PyTuple_GET_SIZE(args) == 0)
        return do_strip(self, LEFTSTRIP); /* Common case */
    else
        return do_argstrip(self, LEFTSTRIP, args);
}
{% endhighlight %}


#### max(string), min(string)
string中最大最小的字符  


#### string.partition(str)
从str出现的第一个位置起，把字符串string分为一个3元素的元组(string_pre_str,str,string_post_str),如果string中不包含str，则string_pre_str=string, str和string_post_str都为空  
{% highlight c %}
static PyObject *
string_partition(PyStringObject *self, PyObject *sep_obj)
{
    const char *sep;
    Py_ssize_t sep_len;

    if (PyString_Check(sep_obj)) {
        sep = PyString_AS_STRING(sep_obj);
        sep_len = PyString_GET_SIZE(sep_obj);
    }
#ifdef Py_USING_UNICODE
    else if (PyUnicode_Check(sep_obj))
        return PyUnicode_Partition((PyObject *) self, sep_obj);
#endif
    else if (PyObject_AsCharBuffer(sep_obj, &sep, &sep_len))
        return NULL;

    return stringlib_partition(
        (PyObject*) self,
        PyString_AS_STRING(self), PyString_GET_SIZE(self),
        sep_obj, sep, sep_len
        );
}

{% endhighlight %}


#### string.replace(str1, str2, num=string.count(str1))
把string中的str1替换成str2，如果num指定，则替换不超过num次  
{% highlight c %}
static PyObject *
string_replace(PyStringObject *self, PyObject *args)
{
    Py_ssize_t count = -1;
    PyObject *from, *to;
    const char *from_s, *to_s;
    Py_ssize_t from_len, to_len;

    if (!PyArg_ParseTuple(args, "OO|n:replace", &from, &to, &count))
        return NULL;

    if (PyString_Check(from)) {
        from_s = PyString_AS_STRING(from);
        from_len = PyString_GET_SIZE(from);
    }
#ifdef Py_USING_UNICODE
    if (PyUnicode_Check(from))
        return PyUnicode_Replace((PyObject *)self,
                                 from, to, count);
#endif
    else if (PyObject_AsCharBuffer(from, &from_s, &from_len))
        return NULL;

    if (PyString_Check(to)) {
        to_s = PyString_AS_STRING(to);
        to_len = PyString_GET_SIZE(to);
    }
#ifdef Py_USING_UNICODE
    else if (PyUnicode_Check(to))
        return PyUnicode_Replace((PyObject *)self,
                                 from, to, count);
#endif
    else if (PyObject_AsCharBuffer(to, &to_s, &to_len))
        return NULL;

    return (PyObject *)replace((PyStringObject *) self,
                               from_s, from_len,
                               to_s, to_len, count);
}
{% endhighlight %}


#### string.rfind(str, beg=0, end=len(string))
类似于find，不过是从右边开始查找  
{% highlight c %}
static PyObject *
string_rfind(PyStringObject *self, PyObject *args)
{
    Py_ssize_t result = string_find_internal(self, args, -1);
    if (result == -2)
        return NULL;
    return PyInt_FromSsize_t(result);
}
{% endhighlight %}


#### string.rindex(str, beg=0, end=len(string))
类似于index，不过从右边开始查找  
{% highlight c %}
static PyObject *
string_rindex(PyStringObject *self, PyObject *args)
{
    Py_ssize_t result = string_find_internal(self, args, -1);
    if (result == -2)
        return NULL;
    if (result == -1) {
        PyErr_SetString(PyExc_ValueError,
                        "substring not found");
        return NULL;
    }
    return PyInt_FromSsize_t(result);
}
{% endhighlight %}

#### string.rjust(width)
返回一个原字符串右对齐，并使用空格填充至长度width的新字符串  
{% highlight c %}
static PyObject *
string_rjust(PyStringObject *self, PyObject *args)
{
    Py_ssize_t width;
    char fillchar = ' ';

    if (!PyArg_ParseTuple(args, "n|c:rjust", &width, &fillchar))
        return NULL;

    if (PyString_GET_SIZE(self) >= width && PyString_CheckExact(self)) {
        Py_INCREF(self);
        return (PyObject*) self;
    }

    return pad(self, width - PyString_GET_SIZE(self), 0, fillchar);
}
{% endhighlight %}


#### string.rpartition(str)
类似于partition，不过是从string的右边开始查找
{% highlight c %}
static PyObject *
string_rpartition(PyStringObject *self, PyObject *sep_obj)
{
    const char *sep;
    Py_ssize_t sep_len;

    if (PyString_Check(sep_obj)) {
        sep = PyString_AS_STRING(sep_obj);
        sep_len = PyString_GET_SIZE(sep_obj);
    }
#ifdef Py_USING_UNICODE
    else if (PyUnicode_Check(sep_obj))
        return PyUnicode_RPartition((PyObject *) self, sep_obj);
#endif
    else if (PyObject_AsCharBuffer(sep_obj, &sep, &sep_len))
        return NULL;

    return stringlib_rpartition(
        (PyObject*) self,
        PyString_AS_STRING(self), PyString_GET_SIZE(self),
        sep_obj, sep, sep_len
        );
}
{% endhighlight %}


#### string.rstrip
删除string末尾的空格
{% highlight c %}
static PyObject *
string_rstrip(PyStringObject *self, PyObject *args)
{
    if (PyTuple_GET_SIZE(args) == 0)
        return do_strip(self, RIGHTSTRIP); /* Common case */
    else
        return do_argstrip(self, RIGHTSTRIP, args);
}
{% endhighlight %}

#### string.rsplit(str="", num=string.count(str))
从右往左分隔字符串,返回的元组顺序还是从左往右   
{% highlight c %}
static PyObject *
string_rsplit(PyStringObject *self, PyObject *args)
{
    Py_ssize_t len = PyString_GET_SIZE(self), n;
    Py_ssize_t maxsplit = -1;
    const char *s = PyString_AS_STRING(self), *sub;
    PyObject *subobj = Py_None;

    if (!PyArg_ParseTuple(args, "|On:rsplit", &subobj, &maxsplit))
        return NULL;
    if (maxsplit < 0)
        maxsplit = PY_SSIZE_T_MAX;
    if (subobj == Py_None)
        return stringlib_rsplit_whitespace((PyObject*) self, s, len, maxsplit);
    if (PyString_Check(subobj)) {
        sub = PyString_AS_STRING(subobj);
        n = PyString_GET_SIZE(subobj);
    }
#ifdef Py_USING_UNICODE
    else if (PyUnicode_Check(subobj))
        return PyUnicode_RSplit((PyObject *)self, subobj, maxsplit);
#endif
    else if (PyObject_AsCharBuffer(subobj, &sub, &n))
        return NULL;

    return stringlib_rsplit((PyObject*) self, s, len, sub, n, maxsplit);
}
{% endhighlight %}  

{% highlight python %}
str = "Learning string"
str.rsplit('n', 1)
>> ['Learning stri', 'g']
{% endhighlight %}



#### string.split(str="",num=string.count(str))
通过指定的字符串str分隔符对字符串进行切片，如果参数有num指定值，则仅分隔num个子字符串  
{% highlight c %}
static PyObject *
string_split(PyStringObject *self, PyObject *args)
{
    Py_ssize_t len = PyString_GET_SIZE(self), n;
    Py_ssize_t maxsplit = -1;
    const char *s = PyString_AS_STRING(self), *sub;
    PyObject *subobj = Py_None;

    if (!PyArg_ParseTuple(args, "|On:split", &subobj, &maxsplit))
        return NULL;
    if (maxsplit < 0)
        maxsplit = PY_SSIZE_T_MAX;
    if (subobj == Py_None)
        return stringlib_split_whitespace((PyObject*) self, s, len, maxsplit);
    if (PyString_Check(subobj)) {
        sub = PyString_AS_STRING(subobj);
        n = PyString_GET_SIZE(subobj);
    }
#ifdef Py_USING_UNICODE
    else if (PyUnicode_Check(subobj))
        return PyUnicode_Split((PyObject *)self, subobj, maxsplit);
#endif
    else if (PyObject_AsCharBuffer(subobj, &sub, &n))
        return NULL;

    return stringlib_split((PyObject*) self, s, len, sub, n, maxsplit);
}
{% endhighlight %}


#### string.splitlines([keepends])
按照行('\r', '\n', '\r\n')分隔，返回一个包含各行作为元素的列表，如果参数keepends为False，不包含换行符，如果为True，则保留换行符  
{% highlight c %}
static PyObject*
string_splitlines(PyStringObject *self, PyObject *args)
{
    int keepends = 0;

    if (!PyArg_ParseTuple(args, "|i:splitlines", &keepends))
        return NULL;

    return stringlib_splitlines(
        (PyObject*) self, PyString_AS_STRING(self), PyString_GET_SIZE(self),
        keepends
    );
}

{% endhighlight %}  

#### string.swapcase
翻转string中的大小写   
{% highlight c%}
static PyObject *
string_swapcase(PyStringObject *self)
{
    char *s = PyString_AS_STRING(self), *s_new;
    Py_ssize_t i, n = PyString_GET_SIZE(self);
    PyObject *newobj;

    newobj = PyString_FromStringAndSize(NULL, n);
    if (newobj == NULL)
        return NULL;
    s_new = PyString_AsString(newobj);
    for (i = 0; i < n; i++) {
        int c = Py_CHARMASK(*s++);
        if (islower(c)) {
            *s_new = toupper(c);
        }
        else if (isupper(c)) {
            *s_new = tolower(c);
        }
        else
            *s_new = c;
        s_new++;
    }
    return newobj;
}
{% endhighlight %}

#### string.title
返回"标题化"字符串，就是说所有单词都是以大写开始，其余字母否是小写
{% highlight c%}
static PyObject*
string_title(PyStringObject *self)
{
    char *s = PyString_AS_STRING(self), *s_new;
    Py_ssize_t i, n = PyString_GET_SIZE(self);
    int previous_is_cased = 0;
    PyObject *newobj;

    newobj = PyString_FromStringAndSize(NULL, n);
    if (newobj == NULL)
        return NULL;
    s_new = PyString_AsString(newobj);
    for (i = 0; i < n; i++) {
        int c = Py_CHARMASK(*s++);
        if (islower(c)) {
            if (!previous_is_cased)
                c = toupper(c);
            previous_is_cased = 1;
        } else if (isupper(c)) {
            if (previous_is_cased)
                c = tolower(c);
            previous_is_cased = 1;
        } else
            previous_is_cased = 0;
        *s_new++ = c;
    }
    return newobj;
}
{% endhighlight %}


#### string.translate(table, del="")
根据参数str给出的表（包含256个字符）转换字符串中的字符没要过滤掉的字符放到del参数中。  
table  翻译表，是通过maketrans方法转换过而来  
deletechars  字符串中要过滤的字符列表  
{% highlight c %}
static PyObject *
string_translate(PyStringObject *self, PyObject *args)
{
    register char *input, *output;
    const char *table;
    register Py_ssize_t i, c, changed = 0;
    PyObject *input_obj = (PyObject*)self;
    const char *output_start, *del_table=NULL;
    Py_ssize_t inlen, tablen, dellen = 0;
    PyObject *result;
    int trans_table[256];
    PyObject *tableobj, *delobj = NULL;

    if (!PyArg_UnpackTuple(args, "translate", 1, 2,
                          &tableobj, &delobj))
        return NULL;

    if (PyString_Check(tableobj)) {
        table = PyString_AS_STRING(tableobj);
        tablen = PyString_GET_SIZE(tableobj);
    }
    else if (tableobj == Py_None) {
        table = NULL;
        tablen = 256;
    }
#ifdef Py_USING_UNICODE
    else if (PyUnicode_Check(tableobj)) {
        /* Unicode .translate() does not support the deletechars
           parameter; instead a mapping to None will cause characters
           to be deleted. */
        if (delobj != NULL) {
            PyErr_SetString(PyExc_TypeError,
            "deletions are implemented differently for unicode");
            return NULL;
        }
        return PyUnicode_Translate((PyObject *)self, tableobj, NULL);
    }
#endif
    else if (PyObject_AsCharBuffer(tableobj, &table, &tablen))
        return NULL;

    if (tablen != 256) {
        PyErr_SetString(PyExc_ValueError,
          "translation table must be 256 characters long");
        return NULL;
    }

    if (delobj != NULL) {
        if (PyString_Check(delobj)) {
            del_table = PyString_AS_STRING(delobj);
            dellen = PyString_GET_SIZE(delobj);
        }
#ifdef Py_USING_UNICODE
        else if (PyUnicode_Check(delobj)) {
            PyErr_SetString(PyExc_TypeError,
            "deletions are implemented differently for unicode");
            return NULL;
        }
#endif
        else if (PyObject_AsCharBuffer(delobj, &del_table, &dellen))
            return NULL;
    }
    else {
        del_table = NULL;
        dellen = 0;
    }

    inlen = PyString_GET_SIZE(input_obj);
    result = PyString_FromStringAndSize((char *)NULL, inlen);
    if (result == NULL)
        return NULL;
    output_start = output = PyString_AsString(result);
    input = PyString_AS_STRING(input_obj);

    if (dellen == 0 && table != NULL) {
        /* If no deletions are required, use faster code */
        for (i = inlen; --i >= 0; ) {
            c = Py_CHARMASK(*input++);
            if (Py_CHARMASK((*output++ = table[c])) != c)
                changed = 1;
        }
        if (changed || !PyString_CheckExact(input_obj))
            return result;
        Py_DECREF(result);
        Py_INCREF(input_obj);
        return input_obj;
    }

    if (table == NULL) {
        for (i = 0; i < 256; i++)
            trans_table[i] = Py_CHARMASK(i);
    } else {
        for (i = 0; i < 256; i++)
            trans_table[i] = Py_CHARMASK(table[i]);
    }

    for (i = 0; i < dellen; i++)
        trans_table[(int) Py_CHARMASK(del_table[i])] = -1;

    for (i = inlen; --i >= 0; ) {
        c = Py_CHARMASK(*input++);
        if (trans_table[c] != -1)
            if (Py_CHARMASK(*output++ = (char)trans_table[c]) == c)
                continue;
        changed = 1;
    }
    if (!changed && PyString_CheckExact(input_obj)) {
        Py_DECREF(result);
        Py_INCREF(input_obj);
        return input_obj;
    }
    /* Fix the size of the resulting string */
    if (inlen > 0 && _PyString_Resize(&result, output - output_start))
        return NULL;
    return result;
}
{% endhighlight %}

{% highlight python %}
from string import maketrans

intab = "aeiou"
outtab = "12345"
trantab = naketrans(intab, outtab)

str = "this is string example ...wow!!!"

print str.translate(trantab, 'xm')

>> th3s 3s str3ng 21p12 ...w4w!!!
{% endhighlight %}  



#### string.upper
转换string中的小写字母为大写
{% highlight c %}
static PyObject *
string_upper(PyStringObject *self)
{
    char *s;
    Py_ssize_t i, n = PyString_GET_SIZE(self);
    PyObject *newobj;

    newobj = PyString_FromStringAndSize(NULL, n);
    if (!newobj)
        return NULL;

    s = PyString_AS_STRING(newobj);

    Py_MEMCPY(s, PyString_AS_STRING(self), n);

    for (i = 0; i < n; i++) {
        int c = Py_CHARMASK(s[i]);
        if (islower(c))
            s[i] = _toupper(c);
    }

    return newobj;
}
{% endhighlight %}
