---
layout: article
title: "python winreg模块"
categories: python
#excerpt:
tags: [winreg, python]
image:
    teaser: /teaser/reg.jpg
date: 2018-03-25T11:04:00+01:00
---

\_winreg用法，python用于操作windows注册表模块.

#### CreateKey
参数1： obKey 注册表key对象   
参数2：subKey 字符串对象，子key的名称   
{% highlight c %}
static PyObject *
PyCreateKey(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    char *subKey;
    HKEY retKey;
    long rc;
    if (!PyArg_ParseTuple(args, "Oz:CreateKey", &obKey, &subKey))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;
    rc = RegCreateKey(hKey, subKey, &retKey);
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc, "CreateKey");
    return PyHKEY_FromHKEY(retKey);
}
{% endhighlight %}

{% highlight python %}
import _winreg
key = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, r"Software\\Extensions")
{% endhighlight %}


#### CreateKeyEx
参数1： obKey 注册表键对象   
参数2：subKey 字符串，健名称   
参数3：res    
参数4： sam 表示访问权限   
{% highlight c %}
static PyObject *
PyCreateKeyEx(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    char *subKey;
    HKEY retKey;
    int res = 0;
    REGSAM sam = KEY_WRITE;
    long rc;
    if (!PyArg_ParseTuple(args, "Oz|ii:CreateKeyEx", &obKey, &subKey,
                                              &res, &sam))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;

    rc = RegCreateKeyEx(hKey, subKey, res, NULL, (DWORD)NULL,
                                            sam, NULL, &retKey, NULL);
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc, "CreateKeyEx");
    return PyHKEY_FromHKEY(retKey);
}
{% endhighlight %}


#### DeleteKey
参数1：已经打开的key   
参数2：需要删除的key的名称，不能为None，key可能没有子key   
方法不能删除带有子key的keys。删除成功的话，整个key包含值回忆起被删掉，如果失败，会有一个WindowsError异常   
{% highlight c %}
static PyObject *
PyDeleteKey(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    char *subKey;
    long rc;
    if (!PyArg_ParseTuple(args, "Os:DeleteKey", &obKey, &subKey))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;
    rc = RegDeleteKey(hKey, subKey );
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc, "RegDeleteKey");
    Py_INCREF(Py_None);
    return Py_None;
}
{% endhighlight %}

#### DeleteKeyEx
参数1：obKey  
参数2：需要删除的子key，字符串类型，不能为None，可能没有subkeys  
参数3: sam访问权限，可无  
参数4：res预留字段，必须为0，默认值为0，可无  

{% highlight c %}
static PyObject *
PyDeleteKeyEx(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    HMODULE hMod;
    typedef LONG (WINAPI *RDKEFunc)(HKEY, const char*, REGSAM, int);
    RDKEFunc pfn = NULL;
    char *subKey;
    long rc;
    int res = 0;
    REGSAM sam = KEY_WOW64_64KEY;

    if (!PyArg_ParseTuple(args, "Os|ii:DeleteKeyEx",
                                              &obKey, &subKey, &sam, &res))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;

    /* Only available on 64bit platforms, so we must load it
       dynamically. */
    hMod = GetModuleHandle("advapi32.dll");
    if (hMod)
        pfn = (RDKEFunc)GetProcAddress(hMod,
                                                                   "RegDeleteKeyExA");
    if (!pfn) {
        PyErr_SetString(PyExc_NotImplementedError,
                                        "not implemented on this platform");
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    rc = (*pfn)(hKey, subKey, sam, res);
    Py_END_ALLOW_THREADS

    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc, "RegDeleteKeyEx");
    Py_INCREF(Py_None);
    return Py_None;
}
{% endhighlight %}


#### DeleteValue
参数1：一个已经打开的key  
参数2：value 字符串  
{% highlight c %}
static PyObject *
PyDeleteValue(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    char *subKey;
    long rc;
    if (!PyArg_ParseTuple(args, "Oz:DeleteValue", &obKey, &subKey))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    rc = RegDeleteValue(hKey, subKey);
    Py_END_ALLOW_THREADS
    if (rc !=ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc,
                                                   "RegDeleteValue");
    Py_INCREF(Py_None);
    return Py_None;
}
{% endhighlight %}

#### ConnectRegistry
在另一台机器上建立一个预定义的注册表句柄连接，返回一个句柄对象。    
参数1： 另外一台机器的ip或者机器名    
参数2： 一个要打开的key  ，必须是HKEY_CURRENT_USER,HKEY_LOCAL_MACHINE等预先定义好的值，拿到返回的key后就可以进行操作   
{% highlight c %}
static PyObject *
PyConnectRegistry(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    char *szCompName = NULL;
    HKEY retKey;
    long rc;
    if (!PyArg_ParseTuple(args, "zO:ConnectRegistry", &szCompName, &obKey))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    rc = RegConnectRegistry(szCompName, hKey, &retKey);
    Py_END_ALLOW_THREADS
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc,
                                                   "ConnectRegistry");
    return PyHKEY_FromHKEY(retKey);
}
{% endhighlight %}

{% highlight python %}
import _winreg
key = _winreg.ConnectRegisty("IP地址或者机器名", _winreg.HKEY_CURRENT_USER)
{% endhighlight %}

#### DisableReflectionKey
禁止一个32位的进程运行在64位的操作系统上时注册表的映射
{% highlight c %}
static PyObject *
PyDisableReflectionKey(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    HMODULE hMod;
    typedef LONG (WINAPI *RDRKFunc)(HKEY);
    RDRKFunc pfn = NULL;
    LONG rc;

    if (!PyArg_ParseTuple(args, "O:DisableReflectionKey", &obKey))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;

    /* Only available on 64bit platforms, so we must load it
       dynamically. */
    hMod = GetModuleHandle("advapi32.dll");
    if (hMod)
        pfn = (RDRKFunc)GetProcAddress(hMod,
                                       "RegDisableReflectionKey");
    if (!pfn) {
        PyErr_SetString(PyExc_NotImplementedError,
                        "not implemented on this platform");
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    rc = (*pfn)(hKey);
    Py_END_ALLOW_THREADS
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc,
                                                   "RegDisableReflectionKey");
    Py_INCREF(Py_None);
    return Py_None;
}
{% endhighlight %}


#### EnableReflectionKey
为指定的残值回复注册表反射   
{% highlight c %}
static PyObject *
PyEnableReflectionKey(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    HMODULE hMod;
    typedef LONG (WINAPI *RERKFunc)(HKEY);
    RERKFunc pfn = NULL;
    LONG rc;

    if (!PyArg_ParseTuple(args, "O:EnableReflectionKey", &obKey))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;

    /* Only available on 64bit platforms, so we must load it
       dynamically. */
    hMod = GetModuleHandle("advapi32.dll");
    if (hMod)
        pfn = (RERKFunc)GetProcAddress(hMod,
                                       "RegEnableReflectionKey");
    if (!pfn) {
        PyErr_SetString(PyExc_NotImplementedError,
                        "not implemented on this platform");
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    rc = (*pfn)(hKey);
    Py_END_ALLOW_THREADS
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc,
                                                   "RegEnableReflectionKey");
    Py_INCREF(Py_None);
    return Py_None;
}
{% endhighlight %}


#### EnumKey
枚举子key
参数1：已经打开的key   
参数2：子key的索引   
{% highlight c %}
static PyObject *
PyEnumKey(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    int index;
    long rc;
    PyObject *retStr;

    /* The Windows docs claim that the max key name length is 255
     * characters, plus a terminating nul character.  However,
     * empirical testing demonstrates that it is possible to
     * create a 256 character key that is missing the terminating
     * nul.  RegEnumKeyEx requires a 257 character buffer to
     * retrieve such a key name. */
    char tmpbuf[257];
    DWORD len = sizeof(tmpbuf); /* includes NULL terminator */

    if (!PyArg_ParseTuple(args, "Oi:EnumKey", &obKey, &index))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    rc = RegEnumKeyEx(hKey, index, tmpbuf, &len, NULL, NULL, NULL, NULL);
    Py_END_ALLOW_THREADS
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc, "RegEnumKeyEx");

    retStr = PyString_FromStringAndSize(tmpbuf, len);
    return retStr;  /* can be NULL */
}
{% endhighlight %}


#### EnumValue
枚举一个打开的注册表key，返回一个tuple   
参数1： 一个打开的注册表key   
参数2：key中注册表值的索引   


Index | Meaning
--- | ---
0 | value名称
1 | 值
2 | 值的类型

{% highlight c %}
static PyObject *
PyEnumValue(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    int index;
    long rc;
    char *retValueBuf;
    char *retDataBuf;
    char *tmpBuf;
    DWORD retValueSize, bufValueSize;
    DWORD retDataSize, bufDataSize;
    DWORD typ;
    PyObject *obData;
    PyObject *retVal;

    if (!PyArg_ParseTuple(args, "Oi:EnumValue", &obKey, &index))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;

    if ((rc = RegQueryInfoKey(hKey, NULL, NULL, NULL, NULL, NULL, NULL,
                              NULL,
                              &retValueSize, &retDataSize, NULL, NULL))
        != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc,
                                                   "RegQueryInfoKey");
    ++retValueSize;    /* include null terminators */
    ++retDataSize;
    bufDataSize = retDataSize;
    bufValueSize = retValueSize;
    retValueBuf = (char *)PyMem_Malloc(retValueSize);
    if (retValueBuf == NULL)
        return PyErr_NoMemory();
    retDataBuf = (char *)PyMem_Malloc(retDataSize);
    if (retDataBuf == NULL) {
        PyMem_Free(retValueBuf);
        return PyErr_NoMemory();
    }

    while (1) {
        Py_BEGIN_ALLOW_THREADS
        rc = RegEnumValue(hKey,
                  index,
                  retValueBuf,
                  &retValueSize,
                  NULL,
                  &typ,
                  (BYTE *)retDataBuf,
                  &retDataSize);
        Py_END_ALLOW_THREADS

        if (rc != ERROR_MORE_DATA)
            break;

        bufDataSize *= 2;
        tmpBuf = (char *)PyMem_Realloc(retDataBuf, bufDataSize);
        if (tmpBuf == NULL) {
            PyErr_NoMemory();
            retVal = NULL;
            goto fail;
        }
        retDataBuf = tmpBuf;
        retDataSize = bufDataSize;
        retValueSize = bufValueSize;
    }

    if (rc != ERROR_SUCCESS) {
        retVal = PyErr_SetFromWindowsErrWithFunction(rc,
                                                     "PyRegEnumValue");
        goto fail;
    }
    obData = Reg2Py(retDataBuf, retDataSize, typ);
    if (obData == NULL) {
        retVal = NULL;
        goto fail;
    }
    retVal = Py_BuildValue("sOi", retValueBuf, obData, typ);
    Py_DECREF(obData);
  fail:
    PyMem_Free(retValueBuf);
    PyMem_Free(retDataBuf);
    return retVal;
}
{% endhighlight %}

{% highlight python %}
import _winreg
key = _winreg.OpenKey(_winreg.HKEY_CURRENT_KEY, r"Netease\txm")
try:
	i = 0
	while 1:
		name, value, vtype = _winreg.EnumValue(key, i)
		print name, value
		i += 1
except Exception:
	pass
{% endhighlight %}

#### ExpandEnvironmentStrings
展开环境变量中的引用   
{% highlight c %}
static PyObject *
PyExpandEnvironmentStrings(PyObject *self, PyObject *args)
{
    Py_UNICODE *retValue = NULL;
    Py_UNICODE *src;
    DWORD retValueSize;
    DWORD rc;
    PyObject *o;

    if (!PyArg_ParseTuple(args, "u:ExpandEnvironmentStrings", &src))
        return NULL;

    retValueSize = ExpandEnvironmentStringsW(src, retValue, 0);
    if (retValueSize == 0) {
        return PyErr_SetFromWindowsErrWithFunction(retValueSize,
                                        "ExpandEnvironmentStrings");
    }
    retValue = (Py_UNICODE *)PyMem_Malloc(retValueSize * sizeof(Py_UNICODE));
    if (retValue == NULL) {
        return PyErr_NoMemory();
    }

    rc = ExpandEnvironmentStringsW(src, retValue, retValueSize);
    if (rc == 0) {
        PyMem_Free(retValue);
        return PyErr_SetFromWindowsErrWithFunction(retValueSize,
                                        "ExpandEnvironmentStrings");
    }
    o = PyUnicode_FromUnicode(retValue, wcslen(retValue));
    PyMem_Free(retValue);
    return o;
}
{% endhighlight %}

{% highlight python %}
ExpandEnvironmentStrings(u"%windir%")
>> "C:\\Windows"
{% endhighlight %}

#### FlushKey
将key的所有属性全部写入注册表   
参数1：已经打开的key   
{% highlight c %}
static PyObject *
PyFlushKey(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    long rc;
    if (!PyArg_ParseTuple(args, "O:FlushKey", &obKey))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    rc = RegFlushKey(hKey);
    Py_END_ALLOW_THREADS
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc, "RegFlushKey");
    Py_INCREF(Py_None);
    return Py_None;
}
{% endhighlight %}

#### LoadKey
参数1：一个已经打开的key   
参数2：需要操作的子key的名称   
参数3：文件名称   
从指定的文件中读入子健的信息   
{% highlight c %}
static PyObject *
PyLoadKey(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    char *subKey;
    char *fileName;

    long rc;
    if (!PyArg_ParseTuple(args, "Oss:LoadKey", &obKey, &subKey, &fileName))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;
    Py_BEGIN_ALLOW_THREADS
    rc = RegLoadKey(hKey, subKey, fileName );
    Py_END_ALLOW_THREADS
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc, "RegLoadKey");
    Py_INCREF(Py_None);
    return Py_None;
}

{% endhighlight %}


#### OpenKey
参数1: 一个已经打开的key，注册表有六大健根， HKEY_USERS, HKEY_CURRENT_USE,HKEY_CURRENT_CONFIG,HKEY_CLASSES_ROOT,HKEY_LOCAL_MACHINE, HKEY_DYN_DATA   
参数2: 需要操作的子健   
参数3: 必须为0   
参数4：sam，默认为只读模式，蚕蛹的有KEY_ALL_ACCESS, KEY_WRITE, KEY_READ访问权限，默认为只读   
{% highlight c %}
static PyObject *
PyOpenKey(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;

    char *subKey;
    int res = 0;
    HKEY retKey;
    long rc;
    REGSAM sam = KEY_READ;
    if (!PyArg_ParseTuple(args, "Oz|ii:OpenKey", &obKey, &subKey,
                          &res, &sam))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    rc = RegOpenKeyEx(hKey, subKey, res, sam, &retKey);
    Py_END_ALLOW_THREADS
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc, "RegOpenKeyEx");
    return PyHKEY_FromHKEY(retKey);
}

{% endhighlight %}

#### OpenKeyEx
跟接口OpenKey一致  

#### CloseKey
关闭一个打开的key  
参数1： 一个打开的注册表key  
{% highlight c %}
static PyObject *
PyCloseKey(PyObject *self, PyObject *args)
{
    PyObject *obKey;
    if (!PyArg_ParseTuple(args, "O:CloseKey", &obKey))
        return NULL;
    if (!PyHKEY_Close(obKey))
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}
{% endhighlight %}



#### QueryValue
在注册表中检索一个健的路径  
注册表值有名字，类型，和数据值。这个方法找回一个key的第一个值（名字为NULL）但是API调用的时候不会回type，因此一般用QueryValueEx()   

{% highlight c %}
static PyObject *
PyQueryValue(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    char *subKey;
    long rc;
    PyObject *retStr;
    char *retBuf;
    DWORD bufSize = 0;
    DWORD retSize = 0;
    char *tmp;

    if (!PyArg_ParseTuple(args, "Oz:QueryValue", &obKey, &subKey))
        return NULL;

    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;

    rc = RegQueryValue(hKey, subKey, NULL, &retSize);
    if (rc == ERROR_MORE_DATA)
        retSize = 256;
    else if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc,
                                                   "RegQueryValue");

    bufSize = retSize;
    retBuf = (char *) PyMem_Malloc(bufSize);
    if (retBuf == NULL)
        return PyErr_NoMemory();

    while (1) {
        retSize = bufSize;
        rc = RegQueryValue(hKey, subKey, retBuf, &retSize);
        if (rc != ERROR_MORE_DATA)
            break;

        bufSize *= 2;
        tmp = (char *) PyMem_Realloc(retBuf, bufSize);
        if (tmp == NULL) {
            PyMem_Free(retBuf);
            return PyErr_NoMemory();
        }
        retBuf = tmp;
    }

    if (rc != ERROR_SUCCESS) {
        PyMem_Free(retBuf);
        return PyErr_SetFromWindowsErrWithFunction(rc,
                                                   "RegQueryValue");
    }

    if (retBuf[retSize-1] == '\x00')
        retSize--;
    retStr = PyString_FromStringAndSize(retBuf, retSize);
    if (retStr == NULL) {
        PyMem_Free(retBuf);
        return NULL;
    }
    return retStr;
}
{% endhighlight %}


#### QueryValueEx
找到一个注册表key下的某个指定名字的type和数据值。   
参数1： key一个已经打开的注册表key   
参数2：value_name是一个要查询到注册表值得名字  
返回的是一个2个值得tuple   


Index | Meaning
--- | ---
0 | 注册表项的值
1 | 注册表值得类型


{% highlight c %}
static PyObject *
PyQueryValueEx(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    char *valueName;

    long rc;
    char *retBuf, *tmp;
    DWORD bufSize = 0, retSize;
    DWORD typ;
    PyObject *obData;
    PyObject *result;

    if (!PyArg_ParseTuple(args, "Oz:QueryValueEx", &obKey, &valueName))
        return NULL;

    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;

    rc = RegQueryValueEx(hKey, valueName, NULL, NULL, NULL, &bufSize);
    if (rc == ERROR_MORE_DATA)
        bufSize = 256;
    else if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc,
                                                   "RegQueryValueEx");
    retBuf = (char *)PyMem_Malloc(bufSize);
    if (retBuf == NULL)
        return PyErr_NoMemory();

    while (1) {
        retSize = bufSize;
        rc = RegQueryValueEx(hKey, valueName, NULL, &typ,
                             (BYTE *)retBuf, &retSize);
        if (rc != ERROR_MORE_DATA)
            break;

        bufSize *= 2;
        tmp = (char *) PyMem_Realloc(retBuf, bufSize);
        if (tmp == NULL) {
            PyMem_Free(retBuf);
            return PyErr_NoMemory();
        }
        retBuf = tmp;
    }

    if (rc != ERROR_SUCCESS) {
        PyMem_Free(retBuf);
        return PyErr_SetFromWindowsErrWithFunction(rc,
                                                   "RegQueryValueEx");
    }
    obData = Reg2Py(retBuf, bufSize, typ);
    PyMem_Free((void *)retBuf);
    if (obData == NULL)
        return NULL;
    result = Py_BuildValue("Oi", obData, typ);
    Py_DECREF(obData);
    return result;
}
{% endhighlight %}


#### QueryInfoKey
返回一个key的信息，返回类型是tuple  
参数1： 一个打开的key  

返回结果是一个3个值得tuple   


Index | Meaning
0 | 一个整型，表示key有多少子key
1 | 一个整型，表示key有多少个值
2 | 一个长整型，代表上次修改的时间 

{% highlight c %}
static PyObject *
PyQueryInfoKey(PyObject *self, PyObject *args)
{
  HKEY hKey;
  PyObject *obKey;
  long rc;
  DWORD nSubKeys, nValues;
  FILETIME ft;
  LARGE_INTEGER li;
  PyObject *l;
  PyObject *ret;
  if (!PyArg_ParseTuple(args, "O:QueryInfoKey", &obKey))
    return NULL;
  if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
    return NULL;
  if ((rc = RegQueryInfoKey(hKey, NULL, NULL, 0, &nSubKeys, NULL, NULL,
                            &nValues,  NULL,  NULL, NULL, &ft))
      != ERROR_SUCCESS)
    return PyErr_SetFromWindowsErrWithFunction(rc, "RegQueryInfoKey");
  li.LowPart = ft.dwLowDateTime;
  li.HighPart = ft.dwHighDateTime;
  l = PyLong_FromLongLong(li.QuadPart);
  if (l == NULL)
    return NULL;
  ret = Py_BuildValue("iiO", nSubKeys, nValues, l);
  Py_DECREF(l);
  return ret;
}
{% endhighlight %}


#### QueryReflectionKey
查询一个key的反射状态  
参数1： 一个打开的注册表key   
返回True的话表示反射被禁止    
在32位的操作系统上会抛出NotImplemented异常  
{% highlight c %}
static PyObject *
PyQueryReflectionKey(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    HMODULE hMod;
    typedef LONG (WINAPI *RQRKFunc)(HKEY, BOOL *);
    RQRKFunc pfn = NULL;
    BOOL result;
    LONG rc;

    if (!PyArg_ParseTuple(args, "O:QueryReflectionKey", &obKey))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;

    /* Only available on 64bit platforms, so we must load it
       dynamically. */
    hMod = GetModuleHandle("advapi32.dll");
    if (hMod)
        pfn = (RQRKFunc)GetProcAddress(hMod,
                                       "RegQueryReflectionKey");
    if (!pfn) {
        PyErr_SetString(PyExc_NotImplementedError,
                        "not implemented on this platform");
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    rc = (*pfn)(hKey, &result);
    Py_END_ALLOW_THREADS
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc,
                                                   "RegQueryReflectionKey");
    return PyBool_FromLong(result);
}
{% endhighlight %}


#### SaveKey
参数1： 一个打开的注册表key  
参数2： 文件名称  
保存一个指key和它的所有的子key到文件中。需要管理员权限  
参考： https://stackoverflow.com/questions/30984406/winreg-savekey-error-a-required-privilege-is-not-held-by-the-client
{% highlight c %}
static PyObject *
PySaveKey(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    char *fileName;
    LPSECURITY_ATTRIBUTES pSA = NULL;

    long rc;
    if (!PyArg_ParseTuple(args, "Os:SaveKey", &obKey, &fileName))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;
/*  One day we may get security into the core?
    if (!PyWinObject_AsSECURITY_ATTRIBUTES(obSA, &pSA, TRUE))
        return NULL;
*/
    Py_BEGIN_ALLOW_THREADS
    rc = RegSaveKey(hKey, fileName, pSA );
    Py_END_ALLOW_THREADS
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc, "RegSaveKey");
    Py_INCREF(Py_None);
    return Py_None;
}
{% endhighlight %}


#### SetValue
关联一个key与值   
参数1： 一个打开的注册表key   
参数2： subkey的名称  
参数3： 类型  
参数4： 新的值，子key的默认值    
设置之后类似于文件夹的子文件夹
{% highlight c %}
static PyObject *
PySetValue(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    char *subKey;
    char *str;
    DWORD typ;
    DWORD len;
    long rc;
    PyObject *obStrVal;
    PyObject *obSubKey;
    if (!PyArg_ParseTuple(args, "OOiO:SetValue",
                          &obKey,
                          &obSubKey,
                          &typ,
                          &obStrVal))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;
    if (typ != REG_SZ) {
        PyErr_SetString(PyExc_TypeError,
                        "Type must be _winreg.REG_SZ");
        return NULL;
    }
    /* XXX - need Unicode support */
    str = PyString_AsString(obStrVal);
    if (str == NULL)
        return NULL;
    len = PyString_Size(obStrVal);
    if (obSubKey == Py_None)
        subKey = NULL;
    else {
        subKey = PyString_AsString(obSubKey);
        if (subKey == NULL)
            return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    rc = RegSetValue(hKey, subKey, REG_SZ, str, len+1);
    Py_END_ALLOW_THREADS
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc, "RegSetValue");
    Py_INCREF(Py_None);
    return Py_None;
}
{% endhighlight %}


#### SetValueEx
关一个key与值   
参数1： 一个已经打开的注册表的key  
参数2： subkey的名字字符串，子keyw的值关联。  
参数3： 值得类型    
参数4： res默认值为0  
参数5： value，注册表值得具体内容   
关系类似于文件夹下的文件。     
{% highlight c %}
static PyObject *
PySetValueEx(PyObject *self, PyObject *args)
{
    HKEY hKey;
    PyObject *obKey;
    char *valueName;
    PyObject *obRes;
    PyObject *value;
    BYTE *data;
    DWORD len;
    DWORD typ;

    LONG rc;

    if (!PyArg_ParseTuple(args, "OzOiO:SetValueEx",
                          &obKey,
                          &valueName,
                          &obRes,
                          &typ,
                          &value))
        return NULL;
    if (!PyHKEY_AsHKEY(obKey, &hKey, FALSE))
        return NULL;
    if (!Py2Reg(value, typ, &data, &len))
    {
        if (!PyErr_Occurred())
            PyErr_SetString(PyExc_ValueError,
                     "Could not convert the data to the specified type.");
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    rc = RegSetValueEx(hKey, valueName, 0, typ, data, len);
    Py_END_ALLOW_THREADS
    PyMem_DEL(data);
    if (rc != ERROR_SUCCESS)
        return PyErr_SetFromWindowsErrWithFunction(rc,
                                                   "RegSetValueEx");
    Py_INCREF(Py_None);
    return Py_None;
}
{% endhighlight %}

REG_NONE 0   
REG_SZ 1   
REG_EXPAND_SZ 2   
REG_BINARY 3   
REG_DWORD 4   
REG_DWORD_LITTLE_ENDIAN 4   
REG_DWORD_BIG_ENDIAN 5   
REG_LINK 6   
REG_MULTI_SZ 7    
REG_RESOURCE_LIST 8   
REG_FULL_RESOURCE_DESCRIPTOR 9   
REG_RESOURCE_REQUIREMENTS_LIST 10    
REG_QWORD 11   
REG_QWORD_LITLE_ENDIAN 12    


参考：https://docs.python.org/2/library/_winreg.html
