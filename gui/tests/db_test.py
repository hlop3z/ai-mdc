from gui.database.crud import CRUD


if __name__ == "__main__":
    from gui.database.base import BaseModel
    from gui.database.crud import CRUD
    from sqlalchemy import Column, Integer, String, Boolean, and_, or_, not_
    import asyncio

    # Set up the synchronous database engine and session
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    SQLALCHEMY_DATABASE_URL_ASYNC = "sqlite+aiosqlite:///./test.db"

    crud_sync = CRUD(sync=True)
    crud_async = CRUD(sync=False)

    echo = False

    # Define the User model
    class User(BaseModel):
        __tablename__ = "users"
        name = Column(String, index=True)
        email = Column(String, unique=True, index=True)

    user_id = 1

    engine = crud_sync.engine(SQLALCHEMY_DATABASE_URL, echo=echo)
    session = crud_sync.session(engine)
    db = session()

    def sync_main():
        # Sync CRUD
        user_crud = crud_sync.crud(User)

        # Add a user
        user_crud.create(db, {"name": "John Doe", "email": "johndoe@example.com"})

        # Fetch users with pagination
        users = user_crud.filter(db, page=1, items_per_page=10)
        print(f"Fetched Users: {users}")

        # Soft delete a user
        user_id = users[0].id
        user_crud.soft_delete(db, user_id)
        print(f"User with ID {user_id} soft deleted.")

        # Fetch users with pagination
        users = user_crud.filter(db, page=2, items_per_page=20)

        # Soft delete a user
        user_crud.soft_delete(db, user_id)

    # Create a session (async)
    async def async_main():
        engine = crud_async.engine(SQLALCHEMY_DATABASE_URL_ASYNC, echo=echo)
        session = crud_async.session(engine)
        # Async CRUD operations
        async with session() as db:
            user_crud_async = crud_async.crud(User)

            # Add a user
            await user_crud_async.create(
                db, {"name": "Jane Doe", "email": "janedoe@example.com"}
            )

            # Fetch users with pagination (async)
            users = await user_crud_async.filter(db, page=1, items_per_page=10)
            print(f"Fetched Users (async): {users}")

            # Soft delete a user (async)
            user_id = users[0].id
            await user_crud_async.soft_delete(db, user_id)
            print(f"User with ID {user_id} soft deleted (async).")

    def sync_filter():
        user_crud = crud_sync.crud(User)
        users = user_crud.filter(
            db,
            page=1,
            items_per_page=10,
            conditions=[
                and_(
                    User.name.startswith("J"),
                    # not_(User.deleted_at.isnot(None)),
                )
            ],
        )
        users = [x.to_dict() for x in users]
        for user in users:
            print(f"Fetched User: {user}")

    # Create the tables
    crud_sync.create_all()

    # Sync CRUD
    # sync_main()

    # Async CRUD
    # asyncio.run(async_main())

    # Sync Filter
    sync_filter()
