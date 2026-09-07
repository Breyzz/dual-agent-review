# dual-agent-review
Personal use, a small, private, two-model review and research tool through OpenAI and Anthropic API and saves responses through a local markdown file.

Mainly used for privacy since it goes to these two APIs and no third-party and the two agents don't talk to one another since it's reviewed by you.

# Setup
```
git clone <your-repo-url>
cd dual-agent-review
python -m pip install -r requirements.txt
cp .env.example .env
```

# Edit .env and add your ANTHROPIC_API_KEY and OPENAI_API_KEY. Get keys from console.anthropic.com and platform.openai.com.

Usage:

Review uncommitted changes in the current repo:
```
python agent.py review
```

Review a specific repo, or a branch diff instead of working-tree changes:  
```
python agent.py review --path ../other-repo
python agent.py review --against main
```

Ask a research question:
```
python agent.py ask "What are the tradeoffs between event sourcing and CRUD for this kind of system?"
```

Or use the chat UI:
```python server.py```
Then open http://127.0.0.1:8000. Ask something, and both Claude and GPT reply side by side.
