# Basic User Authentication
#
# Functions:
# 1. Login
# 2. Register new user account
# 3. Generate new User ID
# 4. Support user and admin roles


from pathlib import Path

import pandas as pd


# USERS FILE
USERS_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "users.csv"
)


# LOAD USERS
def load_users():
    """
    Load registered users from users.csv.
    """

    # Create users.csv if it does not exist.
    if not USERS_PATH.exists():

        empty_users = pd.DataFrame(
            columns=[
                "user_id",
                "username",
                "password",
                "role",
            ]
        )

        empty_users.to_csv(
            USERS_PATH,
            index=False
        )

        return empty_users


    users = pd.read_csv(
        USERS_PATH,
        dtype=str
    )


    # Prevent missing values.
    users = users.fillna("")


    # Support older users.csv files
    # that do not contain a role column.
    if "role" not in users.columns:

        users["role"] = "user"

        users.to_csv(
            USERS_PATH,
            index=False
        )


    # If an existing account has
    # an empty role, treat it as user.
    users.loc[
        users["role"].str.strip() == "",
        "role"
    ] = "user"


    return users


# LOGIN
def authenticate(
    username,
    password
):
    """
    Check username and password.

    Returns:
        user_id
        username
        role

    Returns None if login fails.
    """

    users = load_users()


    username = (
        str(username)
        .strip()
        .casefold()
    )


    password = (
        str(password)
        .strip()
    )


    # FIND USER
    match = users[
        (
            users["username"]
            .astype(str)
            .str.strip()
            .str.casefold()
            ==
            username
        )
        &
        (
            users["password"]
            .astype(str)
            .str.strip()
            ==
            password
        )
    ]


    if match.empty:

        return None


    user = match.iloc[0]


    role = (
        str(
            user.get(
                "role",
                "user"
            )
        )
        .strip()
        .casefold()
    )


    if role not in [
        "user",
        "admin",
    ]:

        role = "user"


    return {
        "user_id":
            user["user_id"],

        "username":
            user["username"],

        "role":
            role,
    }


# CHECK USERNAME

def username_exists(
    username
):
    """
    Check whether a username
    already exists.
    """

    users = load_users()


    username = (
        str(username)
        .strip()
        .casefold()
    )


    existing_usernames = (
        users["username"]
        .astype(str)
        .str.strip()
        .str.casefold()
    )


    return (
        username
        in existing_usernames.values
    )


# GENERATE NEXT USER ID
def generate_user_id():
    """
    Generate the next normal User ID.

    Admin IDs are ignored.

    Example:
        Highest User ID = User107
        Next User ID = User108
    """

    users = load_users()


    # Existing project user IDs
    # start from User101 for newer accounts.
    highest_number = 100


    for user_id in users[
        "user_id"
    ].astype(str):

        user_id = (
            user_id
            .strip()
        )


        # Ignore Admin001 and
        # any other non-User IDs.
        if not user_id.startswith(
            "User"
        ):

            continue


        number_part = (
            user_id[
                4:
            ]
        )


        if not number_part.isdigit():

            continue


        user_number = int(
            number_part
        )


        highest_number = max(
            highest_number,
            user_number
        )


    next_number = (
        highest_number
        + 1
    )


    return (
        f"User{next_number:03d}"
    )


# REGISTER NEW USER
def register_user(
    username,
    password
):
    """
    Create a normal user account.

    Registration can only create
    role = user.

    Admin accounts must be created
    manually in users.csv.

    Returns:
        success
        message
        user
    """

    username = (
        str(username)
        .strip()
    )


    password = (
        str(password)
        .strip()
    )


    # VALIDATION
    if not username:

        return (
            False,
            "Username cannot be empty.",
            None,
        )


    if not password:

        return (
            False,
            "Password cannot be empty.",
            None,
        )


    if len(username) < 3:

        return (
            False,
            "Username must contain at least 3 characters.",
            None,
        )


    if len(password) < 4:

        return (
            False,
            "Password must contain at least 4 characters.",
            None,
        )


    if username_exists(
        username
    ):

        return (
            False,
            "Username already exists.",
            None,
        )


    # GENERATE USER ID
    new_user_id = (
        generate_user_id()
    )


    # LOAD CURRENT USERS
    users = load_users()


    # CREATE NORMAL USER
    new_user = pd.DataFrame(
        [
            {
                "user_id":
                    new_user_id,

                "username":
                    username,

                "password":
                    password,

                "role":
                    "user",
            }
        ]
    )


    # SAVE USER
    users = pd.concat(
        [
            users,
            new_user,
        ],
        ignore_index=True
    )


    users.to_csv(
        USERS_PATH,
        index=False
    )


    return (
        True,

        (
            "Account created successfully. "
            f"Your User ID is {new_user_id}."
        ),

        {
            "user_id":
                new_user_id,

            "username":
                username,

            "role":
                "user",
        },
    )


# TEST
if __name__ == "__main__":

    print(
        load_users()
    )