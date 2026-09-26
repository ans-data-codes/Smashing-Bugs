# Smashing Bugs — Project Context for Copilot

## What this is
A hackathon project (Neo4j mini agentic hack) called **Smashing Bugs** — an AI agent
that remembers past bugs and their fixes in a Neo4j graph, so when a new bug is
described, it can find similar past bugs (via shared root cause or technology) and
surface the fix that already worked.

## Stack
- Python
- `neo4j` driver (Python)
- `groq` (LLM API — model: llama-3.3-70b-versatile)
- `python-dotenv` for loading `.env`
- Neo4j AuraDB (free tier) as the database

## Data model
Nodes: `Bug`, `Component`, `RootCause`, `Fix`, `Technology`

Relationships:
- `(Bug)-[:AFFECTS]->(Component)`
- `(Bug)-[:CAUSED_BY]->(RootCause)`
- `(Bug)-[:RESOLVED_BY]->(Fix)`
- `(RootCause)-[:RELATED_TO]->(Technology)`
- `(Component)-[:USES]->(Technology)`

## The core query (find similar past bugs)
```cypher
MATCH (newBug:Bug {id: $bugId})-[:CAUSED_BY]->(rc:RootCause)
WITH newBug, rc
MATCH (similarBug:Bug)-[:CAUSED_BY]->(rc)
WHERE similarBug <> newBug
WITH newBug, similarBug, rc, 'ROOT_CAUSE' AS matchType
UNION
MATCH (newBug:Bug {id: $bugId})-[:AFFECTS]->(c:Component)-[:USES]->(t:Technology)
WITH newBug, t
MATCH (similarBug:Bug)-[:AFFECTS]->(otherComp:Component)-[:USES]->(t)
WHERE similarBug <> newBug
WITH newBug, similarBug, t, 'TECHNOLOGY' AS matchType
WITH newBug, similarBug, matchType
MATCH (similarBug)-[:RESOLVED_BY]->(fix:Fix)
RETURN
  similarBug.id AS similar_bug_id,
  similarBug.severity AS severity,
  similarBug.status AS status,
  matchType AS reason,
  collect(fix.name) AS available_fixes
ORDER BY similarBug.severity DESC
```

## Current goal (in priority order)
1. Get a working connection from Python to the Neo4j Aura instance, confirmed by
   successfully running a simple `MATCH` query against real data.
2. Write a script that: takes a plain-English bug description → asks the Groq LLM
   to identify the likely root cause / technology → runs the query above against
   Neo4j → feeds results back to the LLM → LLM responds in plain English
   referencing the similar past bug and its fix.
3. Make it demoable: two bug descriptions fed in sequence, where the second one
   should surface the first as a related past bug.

## Rules for how to help me
- I am not an experienced developer — explain fixes plainly, don't assume I know
  what's wrong.
- Prioritize getting something working end-to-end over writing "clean"/production
  code — this is a 2-hour hackathon build.
- Never ask me to paste real passwords/API keys into chat — tell me which file
  and line to edit myself instead.
- When debugging, give me one clear diagnostic step at a time rather than several
  options at once.
- Do not rewrite my `.env` file's structure — only tell me what values to swap in.
