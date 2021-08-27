# Simple bot using LongPoll Vk
## Usage:
Create a conf.cfg in krem directory, add to file:
```
[DEFAULT]
id = your_group_id_here_without_quotes
token = your_token_here_without_quotes
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
