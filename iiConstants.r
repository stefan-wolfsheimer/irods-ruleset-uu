# \file
# \brief Constants for the ii rules. If architecture changes, only
# 			this file needs be adapted
#
# \author Paul Frederiks
# \copyright Copyright (c) 2016, Utrecht university. All rights reserved
# \license GPLv3, see LICENSE

# \constant GENQMAXROWS Maximum number of rows returned by an iRODS GenQuery or msiGetMoreRows call
GENQMAXROWS = 256

# \constant IIGROUPPREFIX
IIGROUPPREFIX = "research-"

# \constant IIVAULTPREFIX
IIVAULTPREFIX = "vault-"

# \constant IIXSDCOLLECTION
IIXSDCOLLECTION = UUSYSTEMCOLLECTION ++ "/xsd"

# \constant IIXSLCOLLECTION
IIXSLCOLLECTION = UUSYSTEMCOLLECTION ++ "/xsl"

# \constant IIFORMELEMENTSCOLLECTION
IIFORMELEMENTSCOLLECTION = UUSYSTEMCOLLECTION ++ "/formelements"

# \constant IIXSDDEFAULTNAME Name of the fallback default xsd for ilab
IIXSDDEFAULTNAME = "default.xsd"

# \constant IIFORMELEMENTSDEFAULTNAME
IIFORMELEMENTSDEFAULTNAME = "default.xml"

# \constant IIMETADATAXMLNAME
IIMETADATAXMLNAME = "yoda-metadata.xml"

# \constant IIXSLDEFAULTNAME
IIXSLDEFAULTNAME = "default.xsl"

# \constant IIDATACITEDEFAULTNAME
IIDATACITEXSLDEFAULTNAME = "default2datacite.xsl"

# \constant IILANDINGPAGEXSLDEFAULTNAME
IILANDINGPAGEXSLDEFAULTNAME = "default2landingpage.xsl"

# \constant IIPUBLICATIONCOLLECTION
IIPUBLICATIONCOLLECTION = UUSYSTEMCOLLECTION ++ "/publication"

# \constant IILOCKATTRNAME
IILOCKATTRNAME = UUORGMETADATAPREFIX ++ "lock"

# \constant IISTATUSATTRNAME
IISTATUSATTRNAME = UUORGMETADATAPREFIX ++ "status"

# \constant IIVAULTSTATUSATTRNAME
IIVAULTSTATUSATTRNAME = UUORGMETADATAPREFIX ++ "vault_status"

# \brief all folder STATES
FOLDER = "";
LOCKED = "LOCKED";
SUBMITTED = "SUBMITTED";
ACCEPTED = "ACCEPTED";
REJECTED = "REJECTED";
SECURED = "SECURED";

# \constant IIFOLDERTRANSITIONS
IIFOLDERTRANSITIONS = list((FOLDER, LOCKED),
			   (FOLDER, SUBMITTED),
			   (LOCKED, FOLDER),
			   (LOCKED, SUBMITTED),
			   (SUBMITTED, LOCKED),
			   (SUBMITTED, ACCEPTED),
			   (SUBMITTED, REJECTED),
			   (REJECTED, FOLDER),
			   (ACCEPTED, SECURED),
			   (SECURED, FOLDER))

# \brief all vault package states
INCOMPLETE = "INCOMPLETE"
COMPLETE = "COMPLETE"
UNPUBLISHED = "UNPUBLISHED";
SUBMITTED_FOR_PUBLICATION = "SUBMITTED_FOR_PUBLICATION";
APPROVED_FOR_PUBLICATION = "APPROVED_FOR_PUBLICATION";
PUBLISHED = "PUBLISHED";
DEPUBLISHED = "DEPUBLISHED";

# \constant IIVAULTTRANSITIONS
IIVAULTTRANSITIONS = list((UNPUBLISHED, SUBMITTED_FOR_PUBLICATION),
			  (COMPLETE, SUBMITTED_FOR_PUBLICATION),
			  (SUBMITTED_FOR_PUBLICATION, APPROVED_FOR_PUBLICATION),
			  (SUBMITTED_FOR_PUBLICATION, UNPUBLISHED),
			  (APPROVED_FOR_PUBLICATION, PUBLISHED),
			  (PUBLISHED, DEPUBLISHED))
