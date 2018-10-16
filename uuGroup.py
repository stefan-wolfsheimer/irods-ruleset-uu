# \file      uuGroup.py
# \brief     Functions for group management and group queries.
# \author    Felix Croes
# \author    Lazlo Westerhof
# \copyright Copyright (c) 2018 Utrecht University. All rights reserved.
# \license   GPLv3, see LICENSE.

# \brief Return groups and related data.
#
def getGroupData(callback):
    groups = {}

    # First query: obtain a list of groups with group attributes.
    ret_val = callback.msiMakeGenQuery(
        "USER_GROUP_NAME, META_USER_ATTR_NAME, META_USER_ATTR_VALUE",
        "USER_TYPE = 'rodsgroup'",
        irods_types.GenQueryInp())
    query = ret_val["arguments"][2]

    ret_val = callback.msiExecGenQuery(query, irods_types.GenQueryOut())
    while True:
        result = ret_val["arguments"][1]
        for row in range(result.rowCnt):
            name = result.sqlResult[0].row(row)
            attr = result.sqlResult[1].row(row)
            value = result.sqlResult[2].row(row)

            # Create/update group with this information.
            try:
                group = groups[name]
            except Exception:
                group = {
                    "name": name,
                    "managers": [],
                    "members": [],
                    "read": []
                }
                groups[name] = group
            if attr in ["data_classification", "category", "subcategory"]:
                group[attr] = value
            elif attr == "description":
                # Deal with legacy use of '.' for empty description metadata.
                # See uuGroupGetDescription() in uuGroup.r for correct behavior of the old query interface.
                group[attr] = '' if value == '.' else value
            elif attr == "manager":
                group["managers"].append(value)

        # Continue with this query.
        if result.continueInx == 0:
            break
        ret_val = callback.msiGetMoreRows(query, result, 0)
    callback.msiCloseGenQuery(query, result)

    # Second query: obtain list of groups with memberships.
    ret_val = callback.msiMakeGenQuery(
        "USER_GROUP_NAME, USER_NAME, USER_ZONE",
        "USER_TYPE != 'rodsgroup'",
        irods_types.GenQueryInp())
    query = ret_val["arguments"][2]

    ret_val = callback.msiExecGenQuery(query, irods_types.GenQueryOut())
    while True:
        result = ret_val["arguments"][1]
        for row in range(result.rowCnt):
            name = result.sqlResult[0].row(row)
            user = result.sqlResult[1].row(row)
            zone = result.sqlResult[2].row(row)

            if name != user and name != "rodsadmin" and name != "public":
                user = user + "#" + zone
                if name.startswith("read-"):
                    # Match read-* group with research-* or initial-* group.
                    name = name[5:]
                    try:
                        # Attempt to add to read list of research group.
                        group = groups["research-" + name]
                        group["read"].append(user)
                    except Exception:
                        try:
                            # Attempt to add to read list of initial group.
                            group = groups["initial-" + name]
                            group["read"].append(user)
                        except Exception:
                            pass
                elif not name.startswith("vault-"):
                    # Ardinary group.
                    group = groups[name]
                    group["members"].append(user)

        # Continue with this query.
        if result.continueInx == 0:
            break
        ret_val = callback.msiGetMoreRows(query, result, 0)
    callback.msiCloseGenQuery(query, result)

    return groups.values()


# \brief Get a list of all group categories.
#
def getCategories(callback):
    categories = []

    ret_val = callback.msiMakeGenQuery(
        "META_USER_ATTR_VALUE",
        "USER_TYPE = 'rodsgroup' AND META_USER_ATTR_NAME = 'category'",
        irods_types.GenQueryInp())
    query = ret_val["arguments"][2]

    ret_val = callback.msiExecGenQuery(query, irods_types.GenQueryOut())
    while True:
        result = ret_val["arguments"][1]
        for row in range(result.rowCnt):
            categories.append(result.sqlResult[0].row(row))

        if result.continueInx == 0:
            break
        ret_val = callback.msiGetMoreRows(query, result, 0)
    callback.msiCloseGenQuery(query, result)

    return categories


# \brief Get a list of all subcategories within a given group category.
#
# \param[in] category
#
def getSubcategories(callback, category):
    categories = set()    # Unique subcategories.
    groupCategories = {}  # Group name => { category => .., subcategory => .. }

    # Collect metadata of each group into `groupCategories` until both
    # the category and subcategory are available, then add the subcategory
    # to `categories` if the category name matches.
    ret_val = callback.msiMakeGenQuery(
        "USER_GROUP_NAME, META_USER_ATTR_NAME, META_USER_ATTR_VALUE",
        "USER_TYPE = 'rodsgroup' AND META_USER_ATTR_NAME LIKE '%category'",
        irods_types.GenQueryInp())
    query = ret_val['arguments'][2]

    ret_val = callback.msiExecGenQuery(query, irods_types.GenQueryOut())
    while True:
        result = ret_val['arguments'][1]
        for row in range(result.rowCnt):
            group = result.sqlResult[0].row(row)
            key = result.sqlResult[1].row(row)
            value = result.sqlResult[2].row(row)

            if group not in groupCategories:
                groupCategories[group] = {}

            if key in ['category', 'subcategory']:
                groupCategories[group][key] = value

            if ('category' in groupCategories[group] and
                'subcategory' in groupCategories[group]):
                # Metadata complete, now filter on category.
                if groupCategories[group]['category'] == category:
                    # Bingo, add to the subcategory list.
                    categories.add(groupCategories[group]['subcategory'])

                del groupCategories[group]

        if result.continueInx == 0:
            break
        ret_val = callback.msiGetMoreRows(query, result, 0)
    callback.msiCloseGenQuery(query, result)

    return list(categories)


# \brief Write group data for all users to stdout.
#
def uuGetGroupData(rule_args, callback, rei):
    groups = getGroupData(callback)

    # Convert to json string and write to stdout.
    callback.writeString("stdout", json.dumps(groups))


# \brief Write group data for a single user to stdout.
#
def uuGetUserGroupData(rule_args, callback, rei):
    groups = getGroupData(callback)
    user = rule_args[0] + '#' + rule_args[1]

    # Filter groups (only return groups user is part of), convert to json and write to stdout.
    groups = list(filter(lambda group: user in group["read"] or user in group["members"], groups))
    callback.writeString("stdout", json.dumps(groups))


# \brief Write category list to stdout.
#
def uuGroupGetCategoriesJson(rule_args, callback, rei):
    callback.writeString("stdout", json.dumps(getCategories(callback)))


# \brief Write subcategory list to stdout.
#
def uuGroupGetSubcategoriesJson(rule_args, callback, rei):
    callback.writeString("stdout", json.dumps(getSubcategories(callback, rule_args[0])))
