import pymysql


# Django's MySQL backend imports MySQLdb; PyMySQL provides a compatible API.
pymysql.install_as_MySQLdb()

# Django checks MySQLdb's mysqlclient-style version tuple before loading the
# backend. PyMySQL exposes an older compatibility value despite supporting the
# API Django uses.
pymysql.version_info = (2, 2, 1, "final", 0)
