# Basic User Authentication
#
# Functions:
# 1. Login
# 2. Register new account
# 3. Automatically generate new User ID


from pathlib import Path

import pandas as pd


# =========================================================
# USERS FILE
# =========================================================

USERS_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "users.csv"
)


# =========================================================
# LOAD USERS
# =========================================================

def load_users():
    """
    Load registered users from users.csv.
    """

    # If users.csv does not exist,
    # create an empty file.
    if not USERS_PATH.exists():

        empty_users = pd.DataFrame(
            columns=[
                "user_id",
                "username",
                "password",
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


    # Prevent missing values
    users = users.fillna("")


    return users


# =========================================================
# LOGIN
# =========================================================

def authenticate(
    username,
    password
):
    """
    Check whether username and password
    match an existing account.

    Returns user information if valid.

    Otherwise returns None.
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


    # =====================================================
    # FIND USER
    # =====================================================

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


    return {

        "user_id":
            user["user_id"],

        "username":
            user["username"],
    }


# =========================================================
# CHECK USERNAME
# =========================================================

def username_exists(
    username
):
    """
    Check whether a username
    has already been registered.
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


# =========================================================
# GENERATE NEXT USER ID
# =========================================================

def generate_user_id():
    """
    Generate the next User ID.

    Existing rating users occupy:

    User001 - User100

    Therefore new registered users
    start from User101.
    """

    users = load_users()


    # Always reserve User001 - User100
    # for the generated rating dataset.
    highest_number = 100


    for user_id in users[
        "user_id"
    ].astype(str):

        user_id = (
            user_id
            .strip()
        )


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


# =========================================================
# REGISTER NEW USER
# =========================================================

def register_user(
    username,
    password
):
    """
    Create a new user account.

    Returns:

    success,
    message,
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


    # =====================================================
    # VALIDATION
    # =====================================================

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


    # =====================================================
    # GENERATE USER ID
    # =====================================================

    new_user_id = (
        generate_user_id()
    )


    # =====================================================
    # LOAD CURRENT USERS
    # =====================================================

    users = load_users()


    # =====================================================
    # CREATE NEW USER
    # =====================================================

    new_user = pd.DataFrame(
        [
            {

                "user_id":
                    new_user_id,

                "username":
                    username,

                "password":
                    password,
            }
        ]
    )


    # =====================================================
    # ADD TO USERS FILE
    # =====================================================

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
        },
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        load_users()
    )