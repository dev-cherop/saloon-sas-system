DEFAULT_PERMISSIONS = [
    ("customers:read", "View customers"),
    ("customers:create", "Create customers"),
    ("customers:update", "Update customers"),
    ("customers:delete", "Delete customers"),

    ("services:read", "View services"),
    ("services:create", "Create services"),
    ("services:update", "Update services"),
    ("services:delete", "Delete services"),

    ("reports:read", "View reports"),

    ("users:manage", "Manage business users and roles"),

    ("settings:manage", "Manage business settings"),


    ("loyalty:read", "View loyalty balances and history"),
    ("loyalty:earn", "Award loyalty points"),
    ("loyalty:redeem", "Redeem loyalty points"),
    ("loyalty:manage", "Manage loyalty settings"),


    ("expenses:read", "View expenses and expense reports"),
    ("expenses:create", "Record expenses"),
    ("expenses:update", "Update expenses"),
    ("expenses:delete", "Delete expenses"),

    ("payments:read", "View payments and collection reports"),
    ("payments:create", "Record customer payments"),

    ("workers:read", "View workers"),
    ("workers:create", "Create workers"),
    ("workers:update", "Update workers"),
    ("workers:delete", "Delete workers"),

    ("appointments:read", "View appointments"),
    ("appointments:create", "Create appointments"),
    ("appointments:update", "Update appointments"),
    ("appointments:delete", "Delete appointments"),

    ("coupons:read", "View coupons"),
    ("coupons:create", "Create coupons"),
    ("coupons:update", "Update coupons"),
    ("coupons:delete", "Delete coupons"),

        ("checkout:read", "View checkout sales"),
    ("checkout:create", "Create checkout sales"),
        

]

DEFAULT_SYSTEM_PERMISSIONS = [
    ("system:businesses:create", "Create businesses on the platform"),
    ("system:businesses:read", "View all platform businesses"),
    ("system:businesses:manage", "Manage businesses across the platform"),
    ("system:users:manage", "Manage users at the platform level"),
    ("system:settings:manage", "Manage platform-wide settings"),
]