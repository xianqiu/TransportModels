from setuptools import setup


setup(
    name='transportmodels',
    version=__import__('transportmodels').__version__,
    description="Solve the balanced transportation problem with LP (using ortools).",
    long_description=open("README.md").read(),
    author='qx3501332',
    author_email='x.qiu@qq.com',
    license="MIT License",
    url='https://github.com/xianqiu/TransportModels',
    packages=['transportmodels'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False,
)
