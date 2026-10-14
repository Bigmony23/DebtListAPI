from database import Base, engine
import models  # important: this registers Users, Person and Debt on Base.metadata


def reset():
    Base.metadata.drop_all(bind=engine)    # deletes all tables (and their data)
    Base.metadata.create_all(bind=engine)  # recreates them from the new models
    print("Database reset done")


if __name__ == "__main__":
    reset()