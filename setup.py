from setuptools import setup, find_packages
import os

setup(
    name='rdopkg-tar',
    version='0.0.1',
    packages=find_packages(),

    author='',
    author_email='contact@redhat.com',
    description='',
    license='LGPLv2+',
    keywords='',
    url="https://github.com/red-hat-storage/rdopkg-tar",
    zip_safe = False,
    install_requires='rdopkg',
    dependency_links=[],
    tests_require=[
    ],
    entry_points = dict(
        console_scripts = [
            'rdopkg-tar = rdopkg_tar.tar_changes:main',
        ],
    ),
    classifiers = [
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
