# Database

There is no database connected yet in this version of KesfetPlus.

## Why PostgreSQL, and why later?

PostgreSQL will eventually store things like places, reviews, user
preferences, and business/trust data. We are not adding it yet because:

1. We want to prove the API and AI agent foundation works first, without
   the extra complexity of a database connection.
2. Adding a database too early makes it harder to change our data model
   while we are still figuring out what KesfetPlus needs to store.
3. Keeping this step separate makes each stage of the project easier to
   understand and test on its own.

## What will happen later

- We will add PostgreSQL as a running service (locally, then in the cloud).
- We will define tables for places, reviews, users, and trust scores.
- We will connect FastAPI to PostgreSQL using a library such as SQLAlchemy.

Until then, this folder just holds notes and, later, database scripts
(migrations, schema definitions, etc.).
