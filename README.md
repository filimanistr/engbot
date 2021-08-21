# Simple bot using LongPoll Vk
## Usage:
Create a conf.cfg, add to file:
```
[DEFAULT]
token = your_token_here_without_quotes
```

Edit vk.py, rewrite group_id to your group_id(line 16, in params):
```
'group_id': 'your_group_id_here_with_quotes'
```

Create environment:
```
python -m venv krem
```

On Windows:
```
krem\Scripts\activate.bat
```

On Linux, or MacOS:
```
source krem/bin/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

Run krem.py:
```
python krem.py
```
