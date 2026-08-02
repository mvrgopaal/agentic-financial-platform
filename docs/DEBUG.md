ISSUE #1


That message means your installed FAISS wheel was compiled against NumPy 1.x, but your project currently uses NumPy 2.5.1. This often happens after downgrading FAISS to an older release such as faiss-cpu==1.8.0; that version had a documented NumPy 2 compatibility problem on macOS ARM64.


1. Check what FAISS version is pinned
grep -E "faiss|numpy" pyproject.toml

You may currently see:

"faiss-cpu==1.8.0",
2. Upgrade FAISS back to the current compatible release

Run:

uv remove faiss-cpu
uv add "faiss-cpu>=1.14.3"

Do not add numpy<2.

3. Recreate the virtual environment

This removes any old compiled FAISS files:

rm -rf .venv
uv sync
4. Verify the versions
uv run python -c "import numpy; print('NumPy:', numpy.__version__)"
uv run python -c "import faiss; print('FAISS:', faiss.__version__)"

Expected:

NumPy: 2.5.1
FAISS: 1.14.3

The exact NumPy version may differ slightly, but it should remain 2.x.

5. Rebuild the vector index

Because FAISS was replaced, rebuild your saved index:

rm -rf data/vectorstore
uv run python -m app.rag.test_vectorstore

Then test:

uv run python -m app.rag.test_retriever
Important correction

faiss.get_num_gpus() returning 1 on macOS does not necessarily mean you installed a CUDA GPU version. The PyPI package has not provided a GPU package since FAISS 1.7.3, and macOS uses the CPU build. Therefore, that value should not be used as the main diagnostic.

Your immediate dependency combination should be:





ISSUE #2




The fact that the error still occurs after removing torch and sentence-transformers suggests the conflict is elsewhere (possibly with another dependency or how macOS is loading libomp).

First, let's verify the environment

Please run these commands and paste the output:

uv pip list | grep -E "torch|sentence|faiss|numpy|scikit|scipy|chromadb"

and

uv run python -c "import faiss; print(faiss.__version__)"
Next, let's isolate the problem

Create a file named test_faiss.py in your project root:


Temporary workaround (development only)

If you want to continue learning while we identify the root cause, you can run:

export KMP_DUPLICATE_LIB_OK=TRUE
uv run python -m app.rag.test_retriever

This tells the OpenMP runtime to continue despite the duplicate initialization. I don't recommend it for production, but it's acceptable for local experimentation.

The Big Picture

Your Python program looks like this:


Python
   |
LangChain
   |
FAISS
   |
NumPy
   |
C/C++ Libraries
   |
OpenMP

What is OpenMP?

OpenMP (Open Multi-Processing) is a library that allows C/C++ programs to use multiple CPU cores.

Instead of:

CPU Core 1

Chunk 1
Chunk 2
Chunk 3
Chunk 4

OpenMP does:

Core 1      Core 2      Core 3      Core 4

Chunk 1     Chunk 2     Chunk 3     Chunk 4

Everything runs simultaneously.

This is why AI libraries are fast.

