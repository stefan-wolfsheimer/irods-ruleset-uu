createXmlXsdCollections {
	uuGetUserType("$userNameClient#$rodsZoneClient", *usertype);
	writeLine("stdout", "Usertype: *usertype");

	if (*usertype != "rodsadmin") {
		failmsg(-1, "This script needs to be run by a rodsadmin.");
	}

	*isfound = false;
	foreach(*row in SELECT RESC_NAME WHERE RESC_NAME = *resc) {
		*isfound = true;
	}

	if (!*isfound) {
		writeLine("stdout", "Resource *resc is not found. Please provide a valid resource example:");
		writeLine("stdout", "irule -F ./install-default-xml-for-metadata.r '\*resc=\"irodsResc\"'");
		failmsg(-1, "Aborting. Resource not found");
	}

	# Install system collection
	*isfound = false;
	*systemcoll = "/" ++ $rodsZoneClient ++ UUSYSTEMCOLLECTION;
	foreach(*row in SELECT COLL_NAME WHERE COLL_NAME = *systemcoll) {
		*isfound = true;
	}

	if (*isfound) {
		writeLine("stdout", "System collection found at *systemcoll");
	} else {
		msiCollCreate(*systemcoll, 1, *status);
		writeLine("stdout", "Installed: *systemcoll");
	}

	# Install schemas collection
	*isfound = false;
	*schemasColl = "/" ++ $rodsZoneClient ++ IISCHEMACOLLECTION;
	foreach(*row in SELECT COLL_NAME WHERE COLL_NAME = *schemasColl) {
		*isfound = true;
	}

	if(*isfound) {
		writeLine("stdout", "Schemas collection already exists at: *schemasColl");
	} else {
		msiCollCreate(*schemasColl, 1, *status);
		msiSetACL("default", "admin:read", "public", *schemasColl);
		msiSetACL("default", "admin:inherit", "public", *schemasColl);
		writeLine("stdout", "Installed: *schemasColl");
	}

	# Install schema collection
	*isfound = false;
	*schemaColl = "/" ++ $rodsZoneClient ++ IISCHEMACOLLECTION ++ "/" ++ *default;
	foreach(*row in SELECT COLL_NAME WHERE COLL_NAME = *schemaColl) {
		*isfound = true;
	}

	if(*isfound) {
		writeLine("stdout", "Schema collection already exists at: *schemaColl");
	} else {
		msiCollCreate(*schemaColl, 1, *status);
		msiSetACL("default", "admin:read", "public", *schemaColl);
		msiSetACL("default", "admin:inherit", "public", *schemaColl);
		writeLine("stdout", "Installed: *schemaColl");
	}

        # Install schema for XSD
	*xsdforxsd = *schemasColl ++ "/" ++ "schema-for-xsd.xsd";
	if (uuFileExists(*xsdforxsd)) {
		if (*update == 1) {
			msiDataObjPut(*xsdforxsd, *resc, "localPath=*src/schema-for-xsd.xsd++++forceFlag=", *status);
			writeLine("stdout", "Update: *xsdforxsd");
		} else {
			writeLine("stdout", "Present: *xsdforxsd");
		}
	} else {
		msiDataObjPut(*xsdforxsd, *resc, "localPath=*src/schema-for-xsd.xsd", *status);
		writeLine("stdout", "Installed: *xsdforxsd");
	}

	# Install default research XSD
	*xsddefault = *schemaColl ++ "/" ++ IIRESEARCHXSDNAME;
        *defaultResearchSchema = IIRESEARCHXSDNAME;
        if (uuFileExists(*xsddefault)) {
		if (*update == 1) {
			msiDataObjPut(*xsddefault, *resc, "localPath=*src/*default/*defaultResearchSchema++++forceFlag=", *status);
			writeLine("stdout", "Updated: *xsddefault");
		} else {
			writeLine("stdout", "Present: *xsddefault");
		}
	} else {
		msiDataObjPut(*xsddefault, *resc, "localPath=*src/*default/*defaultResearchSchema", *status);
		writeLine("stdout", "Installed: *xsddefault");
	}

	# Install default vault XSD
	*xsddefault = *schemaColl ++ "/" ++ IIVAULTXSDNAME;
        *defaultVaultSchema = IIVAULTXSDNAME;
        if (uuFileExists(*xsddefault)) {
		if (*update == 1) {
			msiDataObjPut(*xsddefault, *resc, "localPath=*src/*default/*defaultVaultSchema++++forceFlag=", *status);
			writeLine("stdout", "Updated: *xsddefault");
		} else {
			writeLine("stdout", "Present: *xsddefault");
		}
	} else {
		msiDataObjPut(*xsddefault, *resc, "localPath=*src/*default/*defaultVaultSchema", *status);
		writeLine("stdout", "Installed: *xsddefault");
	}

	# Install default XSL (Yoda metadata XML to AVU XML)
	*xsldefault = *schemaColl ++ "/" ++ IIAVUXSLNAME;
	*xsl = IIAVUXSLNAME;
        if (uuFileExists(*xsldefault)) {
		if (*update == 1) {
			msiDataObjPut(*xsldefault, *resc, "localPath=*src/*default/*xsl++++forceFlag=", *status)
			writeLine("stdout", "Updated: *xsldefault");
		} else {
			writeLine("stdout", "Present: *xsldefault");
		}
	} else {
		msiDataObjPut(*xsldefault, *resc, "localPath=*src/*default/*xsl", *status);
		writeLine("stdout", "Installed: *xsldefault");
	}

	# Install DataCite XSL (Yoda metadata XML to DataCite XML)
        *xsldatacite = *schemaColl ++ "/" ++ IIDATACITEXSLNAME;
	*xsl = IIDATACITEXSLNAME;
        if (uuFileExists(*xsldatacite)) {
		if (*update == 1) {
			msiDataObjPut(*xsldatacite, *resc, "localPath=*src/*default/*xsl++++forceFlag=", *status);
			writeLine("stdout", "Updated: *xsldatacite");
		} else {
			writeLine("stdout", "Present: *xsldatacite");
		}
 	} else {
		msiDataObjPut(*xsldatacite, *resc, "localPath=*src/*default/*xsl", *status);
		writeLine("stdout", "Installed: *xsldatacite");
        }

        # Install landingpage XSL (Yoda metadata XML to landingpage HTML)
        *xsllandingpage = *schemaColl ++ "/" ++ IILANDINGPAGEXSLNAME;
	*xsl = IIDATACITEXSLNAME;
        if (uuFileExists(*xsllandingpage)) {
		if (*update == 1) {
			msiDataObjPut(*xsllandingpage, *resc, "localPath=*src/*default/*xsl++++forceFlag=", *status);
 			writeLine("stdout", "Updated: *xsllandingpage");
		} else {
			writeLine("stdout", "Present: *xsllandingpage");
		}
 	} else {
		msiDataObjPut(*xsllandingpage, *resc, "localPath=*src/*default/*xsl", *status);
		writeLine("stdout", "Installed: *xsllandingpage");
        }

        # Install emtpy landingpage XSL (Yoda metadata XML to landingpage HTML)
        *xslemptylandingpage = *schemasColl ++ "/" ++ IIEMPTYLANDINGPAGEXSLNAME;
	*xsl = IIEMPTYLANDINGPAGEXSLNAME;
        if (uuFileExists(*xslemptylandingpage)) {
		if (*update == 1) {
			msiDataObjPut(*xslemptylandingpage, *resc, "localPath=*src/*xsl++++forceFlag=", *status);
			writeLine("stdout", "Updated: *xslemptylandingpage");
		} else {
			writeLine("stdout", "Present: *xslemptylandingpage");
		}
	} else {
		msiDataObjPut(*xslemptylandingpage, *resc, "localPath=*src/*xsl", *status);
		writeLine("stdout", "Installed: *xslemptylandingpage");
        }
}

input *resc="irodsResc", *src="/etc/irods/irods-ruleset-research/tools/schemas", *default="default", *update=0
output ruleExecOut
