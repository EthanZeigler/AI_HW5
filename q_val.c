#include <Python.h>

static PyObject* module_func(PyObject *self, PyObject *args) {
   /* Do your stuff here. */
   self.

   Py_RETURN_NONE;
}

static PyMethodDef module_methods[] = {
   { "q_iteration", (PyCFunction)module_func, METH_VARARGS, NULL },
   { NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC initModule() {
   Py_InitModule3(func, module_methods, "docstring...");
}