from setuptools import setup


packages = [
    'travis_code_reviewers',
    'travis_code_reviewers.readme_scorer',
]

package_dir = {
    'travis_code_reviewers':'.',
    'travis_code_reviewers.readme_scorer':'readme_scorer',
}


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='travis_code_reviewers',
    version='0.1.0',
    description='',
    author='JHA',
    author_email='',
    url='https://github.com/PeterHedleyJHA/travis_code_review',
    packages=packages,
    package_dir=package_dir,
    include_package_data=True,
    install_requires=[x for x in required if not x.startswith('git+')],
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Intended Audience :: Developers',
    ],
    scripts = ['bin/readme_scorer'],
)
