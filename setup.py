from setuptools import setup, find_packages
  
with open('requirements.txt') as f:
    requirements = f.readlines()
  
long_description = 'Tool to perform dynamic terraform applies w/replacement on TFC using resource name keywords.'
  
setup(
        name ='tfc-apply-replace',
        version ='1.0.0',
        author ='Dan Schneider',
        author_email ='djschnei22@gmail.com',
        url ='https://github.com/djschnei21/tfc-ws-apply-replace',
        description ='Tool to perform dynamic terraform applies w/replacement on TFC using resource name keywords.',
        long_description = long_description,
        long_description_content_type ="text/markdown",
        license ='MIT',
        packages = find_packages(),
        entry_points ={
            'console_scripts': [
                'tfc-apply-replace = tfcar.rotate:main'
            ]
        },
        classifiers =(
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ),
        keywords ='tfc terraform-cloud',
        install_requires = requirements,
        zip_safe = False
)