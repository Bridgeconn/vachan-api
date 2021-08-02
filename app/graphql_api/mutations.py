'''GraphQL queries and mutations'''
#pylint: disable=C0302
import graphene
#pylint: disable=E0401
#pylint gives import error if relative import is not used. But app(uvicorn) doesn't accept it
from crud import structurals_crud,contents_crud,projects_crud,nlp_crud
#pylint: disable=E0611
from graphql_api import types, utils
#pylint: disable=C0410
import schemas,schemas_nlp

############ ADD NEW Language #################
class InputAddLang(graphene.InputObjectType):
    """ADD Language Input"""
    language = graphene.String(required=True)
    code = graphene.String(required=True,\
    description="language code as per bcp47(usually 2 letter code)")
    scriptDirection = graphene.String()
    metaData = graphene.JSONString(description="Expecting a dictionary Type")

#pylint: disable=R0901,too-few-public-methods
class AddLanguage(graphene.Mutation):
    """Mutation class for Add Language"""
    class Arguments:
        """Arguments declaration for the mutation"""
        language_addargs = InputAddLang(required=True)

    data = graphene.Field(types.Language)
    message = graphene.String()

#pylint: disable=R0201,no-self-use
#pylint: disable=W0613
    def mutate(self,info,language_addargs):
        '''resolve'''
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (language_addargs,schemas.LanguageCreate)
        result =structurals_crud.create_language(db_,lang=schema_model)
        language = types.Language(
                languageId = result.languageId,
                language = result.language,
                code = result.code,
                scriptDirection = result.scriptDirection,
                metaData = result.metaData
        )
        message = "Language created successfully"
        return UpdateLanguage(message=message,data=language)


####### Update Language ##############
class InputUpdateLang(graphene.InputObjectType):
    """ update Language Input """
    languageId = graphene.Int(required=True)
    language = graphene.String()
    code = graphene.String(description="language code as per bcp47(usually 2 letter code)")
    scriptDirection = graphene.String()
    metaData = graphene.JSONString(description="Expecting a dictionary Type")

class UpdateLanguage(graphene.Mutation):
    """ Mutation for update language"""
    class Arguments:
        """ Argumnets declare for mutations"""
        language_updateargs = InputUpdateLang(required=True)

    data = graphene.Field(types.Language)
    message = graphene.String()

#pylint: disable=R0201,no-self-use
#pylint: disable=W0613
    def mutate(self,info,language_updateargs):
        """resolver"""
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (language_updateargs,schemas.LanguageEdit)
        result = structurals_crud.update_language(db_,lang=schema_model)
        language = types.Language(
                languageId = result.languageId,
                language = result.language,
                code = result.code,
                scriptDirection = result.scriptDirection,
                metaData = result.metaData
        )
        message = "Language edited successfully"
        return UpdateLanguage(message=message,data=language)

########## Add Contents Type ########
class InputContentType(graphene.InputObjectType):
    """ update Language Input """
    contentType = graphene.String(required=True,\
        description="Input object to ceate a new content type : pattern: ^[a-z]+$ :\
        example: commentary")

class CreateContentTypes(graphene.Mutation):
    """Mutation for Content types Creation"""
    class Arguments:
        "mutation arguments"
        content_type = InputContentType(required=True)

    data = graphene.Field(types.ContentType)
    message = graphene.String()

#pylint: disable=R0201,no-self-use
    def mutate(self,info,content_type):
        """resolver"""
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (content_type,schemas.ContentTypeCreate)
        result = structurals_crud.create_content_type(db_,content=schema_model)
        content_type = types.ContentType(
            contentId = result.contentId,
            contentType = result.contentType
        )
        return CreateContentTypes(message = "Content type created successfully"\
            ,data = content_type)

########## Add License ########
enum_val = types.LicensePermission

class InputAddLicense(graphene.InputObjectType):
    """Add license Input"""
    name = graphene.String(required=True)
    code = graphene.String(required=True,\
        description="pattern: '^[a-zA-Z0-9\\.\\_\\-]+$'")
    license = graphene.String(required=True)
    permissions = graphene.List(enum_val, \
        default_value =["Private_use"],\
        description="Expecting a list \
        [ Commercial_use, Modification, Distribution, Patent_use, Private_use ]")

#pylint: disable=R0901,too-few-public-methods
class AddLicense(graphene.Mutation):
    """Mutation class for Add Licenses"""
    class Arguments:
        """Arguments declaration for the mutation"""
        license_args = InputAddLicense(required=True)

    message = graphene.String()
    data = graphene.Field(types.License)

#pylint: disable=R0201,no-self-use
#pylint: disable=W0613
    def mutate(self,info,license_args):
        '''resolve'''
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (license_args,schemas.LicenseCreate)
        result =structurals_crud.create_license(db_,schema_model,user_id=None)
        license_var = types.License(
            name = result.name,
            code = result.code,
            license = result.license,
            permissions = result.permissions,
            active = result.active
        )
        message = "License uploaded successfully"
        return AddLicense(message=message,data=license_var)

########## Edit License ########
enum_val = types.LicensePermission

class InputEditLicense(graphene.InputObjectType):
    """Edit license Input"""
    name = graphene.String()
    code = graphene.String(required=True,description=\
        "pattern: ^[a-zA-Z0-9\\.\\_\\-]+$")
    license = graphene.String()
    permissions = graphene.List(enum_val, default_value =\
        ["Private_use"],\
        description="Expecting a list\
        [ Commercial_use, Modification, Distribution, Patent_use, Private_use ]")
    active = graphene.Boolean()

#pylint: disable=R0901,too-few-public-methods
class EditLicense(graphene.Mutation):
    """Mutation class for Edit Licenses"""
    class Arguments:
        """Arguments declaration for the mutation"""
        license_args = InputEditLicense()

    message = graphene.String()
    data = graphene.Field(types.License)

#pylint: disable=R0201,no-self-use
#pylint: disable=W0613
    def mutate(self,info,license_args):
        '''resolve'''
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (license_args,schemas.LicenseEdit)
        result =structurals_crud.update_license(db_,schema_model,user_id=None)
        license_var = types.License(
            name = result.name,
            code = result.code,
            license = result.license,
            permissions = result.permissions,
            active = result.active
        )
        message = "License edited successfully"
        return AddLicense(message=message,data=license_var)

########## Add Version ########
class InputAddVersion(graphene.InputObjectType):
    """Input for Edit versions"""
    versionAbbreviation = graphene.String(required=True,\
        description="pattern: ^[A-Z]+$")
    versionName = graphene.String(required=True)
    revision = graphene.Int(default_value = 1)
    metaData = graphene.JSONString(default_value = None,\
    description="Expecting a dictionary Type JSON String")

class AddVersion(graphene.Mutation):
    "Mutations for Add Version"
    class Arguments:
        """Arguments for Add Version"""
        version_arg = InputAddVersion()

    message = graphene.String()
    data = graphene.Field(types.Version)

#pylint: disable=R0201,no-self-use
    def mutate(self,info,version_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (version_arg,schemas.VersionCreate)
        result =structurals_crud.create_version(db_,schema_model)
        version_var = types.Version(
            versionId = result.versionId,
            versionAbbreviation = result.versionAbbreviation,
            versionName = result.versionName,
            revision = result.revision,
            metaData = result.metaData
        )
        message = "Version created successfully"
        return AddVersion(message=message,data=version_var)

########## Edit Version ########
class InputEditVersion(graphene.InputObjectType):
    """Input for Edit versions"""
    versionId = graphene.ID(required=True)
    versionAbbreviation = graphene.String(\
        description="pattern: ^[A-Z]+$")
    versionName = graphene.String()
    revision = graphene.Int()
    metaData = graphene.JSONString(description="Expecting a dictionary Type JSON String")

class EditVersion(graphene.Mutation):
    "Mutations for Edit Version"
    class Arguments:
        """Arguments for Edit Version"""
        version_arg = InputEditVersion()

    message = graphene.String()
    data = graphene.Field(types.Version)

#pylint: disable=R0201,no-self-use
    def mutate(self,info,version_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (version_arg,schemas.VersionEdit)
        result =structurals_crud.update_version(db_,schema_model)
        version_var = types.Version(
            versionId = result.versionId,
            versionAbbreviation = result.versionAbbreviation,
            versionName = result.versionName,
            revision = result.revision,
            metaData = result.metaData
        )
        message = "Version edited successfully"
        return EditVersion(message=message,data=version_var)

########## Add Source ########
class InputAddSource(graphene.InputObjectType):
    """Add Source Input"""
    contentType  = graphene.String(required=True)
    language = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    version = graphene.String(required=True,\
        description="pattern:^[A-Z]+$")
    revision = graphene.String(default_value = 1,\
        description="default: 1")
    year = graphene.Int(required=True)
    license = graphene.String(default_value = "CC-BY-SA",\
        description="pattern: ^[a-zA-Z0-9\\.\\_\\-]+$")
    metaData = graphene.JSONString(description="Expecting a dictionary Type JSON String")

class AddSource(graphene.Mutation):
    "Mutations for Add Source"
    class Arguments:
        """Arguments for Add Source"""
        source_arg = InputAddSource()

    message = graphene.String()
    data = graphene.Field(types.Source)

#pylint: disable=R0201,no-self-use
    def mutate(self,info,source_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (source_arg,schemas.SourceCreate)
        source_name = schema_model.language + "_" + schema_model.version + "_" +\
            schema_model.revision + "_" + schema_model.contentType
        result =structurals_crud.create_source(db_,schema_model,source_name,user_id = None)
        source_var = types.Source(
            sourceName = result.sourceName,
            contentType = result.contentType,
            language = result.language,
            version = result.version,
            year = result.year,
            license = result.license,
            metaData = result.metaData,
            active = result.active
        )
        message = "Source created successfully"
        return AddSource(message=message,data=source_var)

########## Edit Sources ########
class InputEditSource(graphene.InputObjectType):
    """Edit Source Input"""
    sourceName = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    contentType  = graphene.String()
    language = graphene.String(description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    version = graphene.String(description="pattern:^[A-Z]+$")
    revision = graphene.String(description="default: 1")
    year = graphene.Int()
    license = graphene.String(description="pattern: ^[a-zA-Z0-9\\.\\_\\-]+$")
    metaData = graphene.JSONString(description="Expecting a dictionary Type JSON String")
    active = graphene.Boolean()

class EditSource(graphene.Mutation):
    "Mutations for Edit Source"
    class Arguments:
        """Arguments for Edit Source"""
        source_arg = InputEditSource()

    message = graphene.String()
    data = graphene.Field(types.Source)

    #pylint: disable=R0201,no-self-use
    def mutate(self,info,source_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (source_arg,schemas.SourceEdit)
        result =structurals_crud.update_source(db_,schema_model,user_id = None)
        source_var = types.Source(
            sourceName = result.sourceName,
            contentType = result.contentType,
            language = result.language,
            version = result.version,
            year = result.year,
            license = result.license,
            metaData = result.metaData,
            active = result.active
        )
        message = "Source edited successfully"
        return AddSource(message=message,data=source_var)

########## Add Bible books ########
class InputBibleDict(graphene.InputObjectType):
    """Add Bible Dict"""
    USFM = graphene.String()
    JSON = graphene.JSONString(description="Provide JSON structure\
         obtained from USFM-Grammar or one like that")

class InputAddBible(graphene.InputObjectType):
    """Add Bible Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    books = graphene.List(InputBibleDict,required=True,\
        description="Must Provide One of the Two USFM or JSON")

class AddBible(graphene.Mutation):
    "Mutations for Add Bible"
    class Arguments:
        """Arguments for Add Bible"""
        bible_arg = InputAddBible()

    message = graphene.String()
    data = graphene.List(types.BibleContent)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,bible_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source =bible_arg.source_name
        books = bible_arg.books
        schema_list = []
        for item in books:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas.BibleBookUpload)
            schema_list.append(schema_model)
        result =contents_crud.upload_bible_books(db_=db_, source_name=source,
        books=schema_list, user_id=None)
        bible_content_list = []
        for item in result:
            bible_var = types.BibleContent(
            book = item.book,
            USFM = item.USFM,
            JSON = item.JSON,
            audio = item.audio,
            active = item.active
            )
            bible_content_list.append(bible_var)
        message = "Bible books uploaded and processed successfully"
        return AddBible(message=message,data=bible_content_list)

########## Edit Bible books ########
class BibleEditDict(graphene.InputObjectType):
    """bible books inputs"""
    book_code = graphene.String(
        description="pattern:^[a-zA-Z1-9][a-zA-Z][a-zA-Z]$")
    USFM = graphene.String(description="USFM Data")
    JSON = graphene.JSONString(description="Provide JSON structure obtained\
        from USFM-Grammar or one like that")
    active = graphene.Boolean(default_value = True)

class InputEditBible(graphene.InputObjectType):
    """Edit Bible Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    books = graphene.List(BibleEditDict,\
        description="Either JSON or USFM should provide")
class EditBible(graphene.Mutation):
    "Mutations for Edit Bible"
    class Arguments:
        """Arguments for Edit Bible"""
        bible_arg = InputEditBible()

    message = graphene.String()
    data = graphene.List(types.BibleContent)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,bible_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source =bible_arg.source_name
        books = bible_arg.books
        schema_list = []
        for item in books:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas.BibleBookEdit)
            schema_list.append(schema_model)
        result =contents_crud.update_bible_books(db_=db_, source_name=source,
        books=schema_list, user_id=None)
        bible_content_list = []
        for item in result:
            bible_var = types.BibleContent(
            book = item.book,
            USFM = item.USFM,
            JSON = item.JSON,
            audio = item.audio,
            active = item.active
            )
            bible_content_list.append(bible_var)
        message = "Bible books updated successfully"
        return AddBible(message=message,data=bible_content_list)

########## Add Audio bible ########
class AudioAdddict(graphene.InputObjectType):
    """audio input"""
    name = graphene.String(required=True)
    url = graphene.String(required=True)
    books = graphene.List(graphene.String,required=True)
    format = graphene.String(required=True)
    active = graphene.Boolean(default_value = True)

class InputAddAudioBible(graphene.InputObjectType):
    """Add Audio Bible Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    audio_data = graphene.List(AudioAdddict)

class AddAudioBible(graphene.Mutation):
    "Mutations for Add Audio Bible"
    class Arguments:
        """Arguments for Add Audio Bible"""
        bible_arg = InputAddAudioBible()

    message = graphene.String()
    data = graphene.List(types.AudioBible)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,bible_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source =bible_arg.source_name
        audio_data = bible_arg.audio_data
        schema_list = []
        for item in audio_data:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas.AudioBibleUpload)
            schema_list.append(schema_model)
        result =contents_crud.upload_bible_audios(db_=db_, source_name=source,
        audios=schema_list, user_id=None)
        audio_content_list = []
        for item in result:
            audio_var = types.AudioBible(
            name = item.name,
            url = item.url,
            format = item.format,
            active = item.active
            )
            audio_content_list.append(audio_var)
        message = "Bible audios details uploaded successfully"
        return AddAudioBible(message=message,data=audio_content_list)

########## Edit Audio bible ########
class AudioEditdict(graphene.InputObjectType):
    """audio input"""
    name = graphene.String()
    url = graphene.String()
    books = graphene.List(graphene.String,required=True)
    format = graphene.String()
    active = graphene.Boolean(default_value = True)

class InputEditAudioBible(graphene.InputObjectType):
    """Edit Audio Bible Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    audio_data = graphene.List(AudioEditdict)

class EditAudioBible(graphene.Mutation):
    "Mutations for Edit Audio Bible"
    class Arguments:
        """Arguments for Edit Audio Bible"""
        bible_arg = InputEditAudioBible()

    message = graphene.String()
    data = graphene.List(types.AudioBible)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,bible_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source =bible_arg.source_name
        audio_data = bible_arg.audio_data
        schema_list = []
        for item in audio_data:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas.AudioBibleEdit)
            schema_list.append(schema_model)
        result =contents_crud.update_bible_audios(db_=db_, source_name=source,
        audios=schema_list, user_id=None)
        audio_content_list = []
        for item in result:
            audio_var = types.AudioBible(
            name = item.name,
            url = item.url,
            format = item.format,
            active = item.active
            )
            audio_content_list.append(audio_var)
        message = "Bible audios details updated successfully"
        return EditAudioBible(message=message,data=audio_content_list)

########## Add Commentaries ########
class CommentaryDict(graphene.InputObjectType):
    """commentary input"""
    bookCode = graphene.String(required=True)
    chapter = graphene.Int(required=True)
    verseStart = graphene.Int()
    verseEnd = graphene.Int()
    commentary = graphene.String(required=True)
    active = graphene.Boolean(default_value = True)

class InputAddCommentary(graphene.InputObjectType):
    """Add commentary Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    commentary_data = graphene.List(CommentaryDict)

class AddCommentary(graphene.Mutation):
    "Mutations for Add Commentary"
    class Arguments:
        """Arguments for Add Commentary"""
        comm_arg = InputAddCommentary()

    message = graphene.String()
    data = graphene.List(types.Commentary)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,comm_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source =comm_arg.source_name
        comm_data = comm_arg.commentary_data
        schema_list = []
        for item in comm_data:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas.CommentaryCreate)
            schema_list.append(schema_model)
        result =contents_crud.upload_commentaries(db_=db_, source_name=source,
        commentaries=schema_list, user_id=None)
        comm_content_list = []
        for item in result:
            comm_var = types.Commentary(
                book = item.book,
                chapter = item.chapter,
                verseStart = item.verseStart,
                verseEnd = item.verseEnd,
                commentary = item.commentary,
                active = item.active
            )
            comm_content_list.append(comm_var)
        message = "Commentaries added successfully"
        return AddCommentary(message=message,data=comm_content_list)

########## Edit Commentaries ########
class CommentaryEditDict(graphene.InputObjectType):
    """commentary Edit input"""
    bookCode = graphene.String(required=True)
    chapter = graphene.Int(required=True)
    verseStart = graphene.Int()
    verseEnd = graphene.Int()
    commentary = graphene.String()
    active = graphene.Boolean(default_value = True)

class InputEditCommentary(graphene.InputObjectType):
    """Edit commentary Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    commentary_data = graphene.List(CommentaryEditDict)

class EditCommentary(graphene.Mutation):
    "Mutations for Edit Commentary"
    class Arguments:
        """Arguments for Edit Commentary"""
        comm_arg = InputEditCommentary()

    message = graphene.String()
    data = graphene.List(types.Commentary)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,comm_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source =comm_arg.source_name
        comm_data = comm_arg.commentary_data
        schema_list = []
        for item in comm_data:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas.CommentaryEdit)
            schema_list.append(schema_model)
        result =contents_crud.update_commentaries(db_=db_, source_name=source,
        commentaries=schema_list, user_id=None)
        comm_content_list = []
        for item in result:
            comm_var = types.Commentary(
                book = item.book,
                chapter = item.chapter,
                verseStart = item.verseStart,
                verseEnd = item.verseEnd,
                commentary = item.commentary,
                active = item.active
            )
            comm_content_list.append(comm_var)
        message = "Commentaries updated successfully"
        return AddCommentary(message=message,data=comm_content_list)

##### AGMT PROJECT MANAGEMENT Create #######
enum_doc = types.TranslationDocumentType

class InputStopWords(graphene.InputObjectType):
    """stopword input for create and update"""
    prepositions = graphene.List(graphene.String,required=True)
    postpositions = graphene.List(graphene.String,required=True)

class InputCreateAGMTProject(graphene.InputObjectType):
    """CreateAGMTProject Input"""
    projectName = graphene.String(required=True,\
        description="example: Hindi Malayalam Gospels")
    sourceLanguageCode = graphene.String(required=True,\
        description="pattern:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    targetLanguageCode = graphene.String(required=True,\
        description="pattern:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    documentFormat = graphene.Field(enum_doc)
    useDataForLearning = graphene.Boolean()
    stopwords = graphene.Field(InputStopWords)
    punctuations = graphene.List(graphene.String,\
        description="""List [ ",", "\"", "!", ".", ":", ";", "\n""]""")
    active = graphene.Boolean(default_value=True)

class CreateAGMTProject(graphene.Mutation):
    "Mutations for CreateAGMTProject"
    class Arguments:
        """Arguments for CreateAGMTProject"""
        agmt_arg = InputCreateAGMTProject()

    message = graphene.String()
    data = graphene.Field(types.TranslationProject)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,agmt_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (agmt_arg,schemas_nlp.TranslationProjectCreate)

        result = projects_crud.create_agmt_project(db_=db_,project=schema_model,user_id=10101)
        comm = types.TranslationProject(
            projectId = result.projectId,
            projectName = result.projectName,
            sourceLanguage = result.sourceLanguage,
            targetLanguage = result.targetLanguage,
            documentFormat = result.documentFormat,
            users = result.users,
            metaData = result.metaData,
            active = result.active
        )
        message = "Project created successfully"
        return CreateAGMTProject(message = message, data = comm)


##### AGMT PROJECT MANAGEMENT EDIT #######

class InputSeclectedBooks(graphene.InputObjectType):
    """List of selected books from an existing bible in the server"""
    bible = graphene.String(required=True,\
        description = "pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$\
        example: hi_IRV_1_bible")
    books = graphene.List(graphene.String,required=True,\
        description = "pattern: ^[a-zA-Z1-9][a-zA-Z][a-zA-Z]$\
        example: [ 'luk', 'jhn' ]")

class InputEditAGMTProject(graphene.InputObjectType):
    """CreateAGMTProject Input"""
    projectId = graphene.Int(required=True)
    projectName = graphene.String(\
        description="example: Hindi Malayalam Gospels")
    selectedBooks = graphene.Field(InputSeclectedBooks)
    uploadedBooks = graphene.List(graphene.String)
    useDataForLearning = graphene.Boolean()
    stopwords = graphene.Field(InputStopWords)
    punctuations = graphene.List(graphene.String,\
        description="""List [ ",", "\"", "!", ".", ":", ";", "\n""]""")
    active = graphene.Boolean(default_value=True)

class EditAGMTProject(graphene.Mutation):
    "Mutations for EditAGMTProject"
    class Arguments:
        """Arguments for EditAGMTProject"""
        agmt_arg = InputEditAGMTProject()

    message = graphene.String()
    data = graphene.Field(types.TranslationProject)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,agmt_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (agmt_arg,schemas_nlp.TranslationProjectEdit)

        result = projects_crud.update_agmt_project(db_=db_,project_obj=schema_model,user_id=10101)
        comm = types.TranslationProject(
            projectId = result.projectId,
            projectName = result.projectName,
            sourceLanguage = result.sourceLanguage,
            targetLanguage = result.targetLanguage,
            documentFormat = result.documentFormat,
            users = result.users,
            metaData = result.metaData,
            active = result.active
        )
        message = "Project updated successfully"
        return EditAGMTProject(message = message, data = comm)


##### AGMT project user #######
class AGMTUserCreateInput(graphene.InputObjectType):
    """input of AGMT user create"""
    project_id = graphene.Int(required=True)
    user_id = graphene.Int(required=True)

class AGMTUserCreate(graphene.Mutation):
    """mutation for AGMT user create"""
    class Arguments:
        """args"""
        agmt_arg = AGMTUserCreateInput()

    message = graphene.String()
    data = graphene.Field(types.ProjectUser)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,agmt_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        project_id = agmt_arg.project_id
        user_id = agmt_arg.user_id
        result = projects_crud.add_agmt_user(db_=db_,project_id=\
            project_id,user_id=user_id,current_user=None)
        comm = types.ProjectUser(
            project_id = result.project_id,
            userId = result.userId,
            userRole = result.userRole,
            metaData = result.metaData,
            active = result.active
        )
        message = "User added in project successfully"
        return AGMTUserCreate(message = message, data = comm)

##### AGMT project user Edit#######
class AGMTUserEditInput(graphene.InputObjectType):
    """input of AGMT user Edit"""
    project_id = graphene.Int(required=True)
    userId = graphene.Int(required=True)
    userRole = graphene.String()
    metaData = graphene.JSONString()
    active = graphene.Boolean()

class AGMTUserEdit(graphene.Mutation):
    """mutation for AGMT user Edit"""
    class Arguments:
        """args"""
        agmt_arg = AGMTUserEditInput()

    message = graphene.String()
    data = graphene.Field(types.ProjectUser)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,agmt_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (agmt_arg,schemas_nlp.ProjectUser)
        result = projects_crud.update_agmt_user(db_=db_,user_obj = schema_model ,current_user=10101)
        comm = types.ProjectUser(
            project_id = result.project_id,
            userId = result.userId,
            userRole = result.userRole,
            metaData = result.metaData,
            active = result.active
        )
        message = "User updated in project successfully"
        return AGMTUserEdit(message = message, data = comm)
########## Add BibleVideo ########
class BibleVideoDict(graphene.InputObjectType):
    """BibleVideo input"""
    title = graphene.String(required=True)
    books = graphene.List(graphene.String,required=True,\
        description="provide book codes")
    videoLink = graphene.String(required=True)
    description = graphene.String(required=True)
    theme = graphene.String(required=True)
    active = graphene.Boolean(default_value = True)

class InputAddBibleVideo(graphene.InputObjectType):
    """Add BibleVideo Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    video_data = graphene.List(BibleVideoDict)

class AddBibleVideo(graphene.Mutation):
    "Mutations for Add BibleVideo"
    class Arguments:
        """Arguments for Add BibleVideo"""
        video_arg = InputAddBibleVideo()

    message = graphene.String()
    data = graphene.List(types.BibleVideo)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,video_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source =video_arg.source_name
        video_data = video_arg.video_data
        schema_list = []
        for item in video_data:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas.BibleVideoUpload)
            schema_list.append(schema_model)
        result =contents_crud.upload_bible_videos(db_=db_, source_name=source,
        videos=schema_list, user_id=None)
        video_content_list = []
        for item in result:
            comm_var = types.BibleVideo(
                title = item.title,
                books = item.books,
                videoLink = item.videoLink,
                description = item.description,
                theme = item.theme,
                active = item.active
            )
            video_content_list.append(comm_var)
        message = "Bible videos added successfully"
        return AddBibleVideo(message=message,data=video_content_list)

########## Edit BibleVideo ########
class BibleVideoEditDict(graphene.InputObjectType):
    """BibleVideo Edit input"""
    title = graphene.String(required=True)
    books = graphene.List(graphene.String)
    videoLink = graphene.String()
    description = graphene.String()
    theme = graphene.String()
    active = graphene.Boolean(default_value = True)

class InputEditBibleVideo(graphene.InputObjectType):
    """Edit BibleVideo Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    video_data = graphene.List(BibleVideoEditDict)

class EditBibleVideo(graphene.Mutation):
    "Mutations for Edit BibleVideo"
    class Arguments:
        """Arguments for Edit BibleVideo"""
        video_arg = InputEditBibleVideo()

    message = graphene.String()
    data = graphene.List(types.BibleVideo)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,video_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source =video_arg.source_name
        video_data = video_arg.video_data
        schema_list = []
        for item in video_data:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas.BibleVideoEdit)
            schema_list.append(schema_model)
        result =contents_crud.update_bible_videos(db_=db_, source_name=source,
        videos=schema_list, user_id=None)
        video_content_list = []
        for item in result:
            comm_var = types.BibleVideo(
                title = item.title,
                books = item.books,
                videoLink = item.videoLink,
                description = item.description,
                theme = item.theme,
                active = item.active
            )
            video_content_list.append(comm_var)
        message = "Bible videos updated successfully"
        return AddBibleVideo(message=message,data=video_content_list)
########## Add Dictionary ########
class DictionaryDict(graphene.InputObjectType):
    """Dictionary input"""
    word = graphene.String(required=True)
    details = graphene.JSONString(description="Expecting a dictionary Type")
    active = graphene.Boolean(default_value = True)

class InputAddDictionary(graphene.InputObjectType):
    """Add Dictionary Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    word_list = graphene.List(DictionaryDict)

class AddDictionary(graphene.Mutation):
    "Mutations for Add Dictionary"
    class Arguments:
        """Arguments for Add Dictionary"""
        dict_arg = InputAddDictionary()

    message = graphene.String()
    data = graphene.List(types.DictionaryWord)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,dict_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source =dict_arg.source_name
        dict_data = dict_arg.word_list
        schema_list = []
        for item in dict_data:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas.DictionaryWordCreate)
            schema_list.append(schema_model)
        result =contents_crud.upload_dictionary_words(db_=db_, source_name=source,
        dictionary_words=schema_list, user_id=None)
        dict_content_list = []
        for item in result:
            dict_var = types.DictionaryWord(
                word = item.word,
                details = item.details,
                active = item.active
            )
            dict_content_list.append(dict_var)
        message = "Dictionary words added successfully"
        return AddDictionary(message=message,data=dict_content_list)

########## Edit Dictionary ########
class DictionaryEditDict(graphene.InputObjectType):
    """Dictionary input"""
    word = graphene.String(required=True)
    details = graphene.JSONString(description="Expecting a dictionary Type")
    active = graphene.Boolean(default_value = True)

class InputEditDictionary(graphene.InputObjectType):
    """Add Dictionary Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    word_list = graphene.List(DictionaryEditDict)

class EditDictionary(graphene.Mutation):
    "Mutations for Edit Dictionary"
    class Arguments:
        """Arguments for Add Dictionary"""
        dict_arg = InputEditDictionary()

    message = graphene.String()
    data = graphene.List(types.DictionaryWord)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,dict_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source =dict_arg.source_name
        dict_data = dict_arg.word_list
        schema_list = []
        for item in dict_data:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas.DictionaryWordEdit)
            schema_list.append(schema_model)
        result =contents_crud.update_dictionary_words(db_=db_, source_name=source,
        dictionary_words=schema_list, user_id=None)
        dict_content_list = []
        for item in result:
            dict_var = types.DictionaryWord(
                word = item.word,
                details = item.details,
                active = item.active
            )
            dict_content_list.append(dict_var)
        message = "Dictionary words updated successfully"
        return EditDictionary(message=message,data=dict_content_list)

########## Add Infographics ########
class InfographicDict(graphene.InputObjectType):
    """Infographic input"""
    bookCode = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z1-9][a-zA-Z][a-zA-Z]$")
    title = graphene.String(required=True)
    infographicLink = graphene.String(required=True,\
        description="Provide valid URL")
    active = graphene.Boolean(default_value = True)

class InputAddInfographic(graphene.InputObjectType):
    """Add Infographic Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    data = graphene.List(InfographicDict)

class AddInfographic(graphene.Mutation):
    "Mutations for Add Infographic"
    class Arguments:
        """Arguments for Add Infographic"""
        info_arg = InputAddInfographic()

    message = graphene.String()
    data = graphene.List(types.Infographic)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,info_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source =info_arg.source_name
        dict_data = info_arg.data
        schema_list = []
        for item in dict_data:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas.InfographicCreate)
            schema_list.append(schema_model)
        result =contents_crud.upload_infographics(db_=db_, source_name=source,
        infographics=schema_list, user_id=None)
        dict_content_list = []
        for item in result:
            dict_var = types.Infographic(
                book = item.book,
                title = item.title,
                infographicLink = item.infographicLink,
                active = item.active
            )
            dict_content_list.append(dict_var)
        message = "Infographics added successfully"
        return AddInfographic(message=message,data=dict_content_list)

########## Edit Infographics ########
class InfographicEditDict(graphene.InputObjectType):
    """Infographic Edit input"""
    bookCode = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z1-9][a-zA-Z][a-zA-Z]$")
    title = graphene.String(required=True)
    infographicLink = graphene.String(\
        description="Provide valid URL")
    active = graphene.Boolean(default_value = True)

class InputEditInfographic(graphene.InputObjectType):
    """Edit Infographic Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    data = graphene.List(InfographicEditDict)

class EditInfographic(graphene.Mutation):
    "Mutations for Edit Infographic"
    class Arguments:
        """Arguments for Edit Infographic"""
        info_arg = InputEditInfographic()

    message = graphene.String()
    data = graphene.List(types.Infographic)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,info_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source =info_arg.source_name
        dict_data = info_arg.data
        schema_list = []
        for item in dict_data:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas.InfographicEdit)
            schema_list.append(schema_model)
        result =contents_crud.update_infographics(db_=db_, source_name=source,
        infographics=schema_list, user_id=None)
        dict_content_list = []
        for item in result:
            dict_var = types.Infographic(
                book = item.book,
                title = item.title,
                infographicLink = item.infographicLink,
                active = item.active
            )
            dict_content_list.append(dict_var)
        message = "Infographics updated successfully"
        return EditInfographic(message=message,data=dict_content_list)

########## Autographa - Translation ########
# Apply token translation
class InputOccurance(graphene.InputObjectType):
    """Input object for applying token translation"""
    sentenceId = graphene.Int(required=True)
    offset = graphene.List(graphene.Int,required=True,\
        description="Max-Min Item 2")

class InputToken(graphene.InputObjectType):
    """Input object for applying token translation"""
    token = graphene.String(required=True)
    occurrences = graphene.List(InputOccurance,required=True)
    translation = graphene.String(required=True)
class InputApplyToken(graphene.InputObjectType):
    """Inputs for Aplly Token"""
    project_id = graphene.Int(required=True)
    return_drafts = graphene.Boolean(default_value = True)
    token = graphene.List(InputToken)

class TokenApply(graphene.Mutation):
    "Mutations for  Token apply"
    class Arguments:
        """Arguments for Token apply"""
        token_arg = InputApplyToken()

    message = graphene.String()
    data = graphene.List(types.Sentence)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,token_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        project_id = token_arg.project_id
        return_drafts = token_arg.return_drafts
        token = token_arg.token

        schema_list = []
        for item in token:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas_nlp.TokenUpdate)
            schema_list.append(schema_model)
        result = nlp_crud.save_agmt_translations(db_=db_,project_id=project_id,\
            token_translations = schema_list,return_drafts = return_drafts,user_id=None)
        dict_content_list = []
        for item in result:
            comm = types.Sentence(
            sentenceId = item.sentenceId,
            sentence = item.sentence,
            draft = item.draft,
            draftMeta = item.draftMeta
            )
            dict_content_list.append(comm)
        message = "Token translations saved"
        return TokenApply(message=message,data=dict_content_list)

# Get Token Sentances
class InputGetSentance(graphene.InputObjectType):
    """Inputs for Aplly Token"""
    project_id = graphene.Int(required=True)
    token = graphene.String(required=True)
    occurance = graphene.List(InputOccurance,required=True)

class GetTokenSentance(graphene.Mutation):
    "Mutations for  Get Token Sentance "
    class Arguments:
        """Arguments for Get token sentance"""
        token_arg = InputGetSentance()

    data = graphene.List(types.Sentence)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,token_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        project_id = token_arg.project_id
        token = token_arg.token
        occurance = token_arg.occurance

        schema_list = []
        for item in occurance:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas_nlp.TokenOccurence)
            schema_list.append(schema_model)
        result = projects_crud.get_agmt_source_per_token(db_=db_,project_id=project_id,\
            token = token, occurrences = schema_list)
        dict_content_list = []
        for item in result:
            comm = types.Sentence(
            sentenceId = item.sentenceId,
            sentence = item.sentence,
            draft = item.draft,
            draftMeta = item.draftMeta
            )
            dict_content_list.append(comm)
        return GetTokenSentance(data=dict_content_list)
#### Translation Suggetions ##########
#Suggeest Auto Translation
class InputAutoTranslation(graphene.InputObjectType):
    """Auto Translation Suggestion input"""
    project_id  = graphene.Int(required=True)
    books = graphene.List(graphene.String)
    sentence_id_list = graphene.List(graphene.Int,\
        description="List of sentance id BCV")
    sentence_id_range = graphene.List(graphene.Int,\
        description="List of sentance range BCV , 2 values in list")
    confirm_all = graphene.Boolean(default_value = False)

class AutoTranslationSuggetion(graphene.Mutation):
    "Mutations for AutoTranslationSuggetion"
    class Arguments:
        """Arguments for AutoTranslationSuggetion"""
        info_arg = InputAutoTranslation()

    data = graphene.List(types.Sentence)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,info_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        project_id  = info_arg.project_id
        books = info_arg.books
        sentence_id_list = info_arg.sentence_id_list
        sentence_id_range = info_arg.sentence_id_range
        confirm_all = info_arg.confirm_all

        result =nlp_crud.agmt_suggest_translations(db_=db_,project_id=project_id,books=books,\
            sentence_id_list=sentence_id_list,sentence_id_range=sentence_id_range,\
            confirm_all=confirm_all)

        dict_content_list = []
        for item in result:
            comm = types.Sentence(
            sentenceId = item.sentenceId,
            sentence = item.sentence,
            draft = item.draft,
            draftMeta = item.draftMeta
            )
            dict_content_list.append(comm)
        return AutoTranslationSuggetion(data=dict_content_list)

#Suggeest  Translation
class InputSentance(graphene.InputObjectType):
    "Sentance Input of translation"
    sentenceId = graphene.String(required=True)
    sentence = graphene.String(required=True)
    draft = graphene.String()
    draftMeta = types.Sentence.draftMeta
    #draftMeta = graphene.List(\
     #   description = "example: List [ List [ List [ 0, 8 ], List [ 0, 8 ], 'confirmed' ],\
      #       List [ List [ 8, 64 ], List [ 8, 64 ], 'untranslated' ] ]")

class InputTranslationData(graphene.InputObjectType):
    """Body content for transaltion"""
    sentacne_list = graphene.List(InputSentance,required=True)
    stopwords = graphene.Field(InputStopWords)
    punctuations = graphene.List(graphene.String,\
        description="""List [ ",", "\"", "!", ".", ":", ";", "\n""]""")

class InputTranslation(graphene.InputObjectType):
    """Translation Suggestion input"""
    source_language = graphene.String(required=True,\
        description="patten:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    target_language  = graphene.String(required=True,\
        description="patten:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    data = graphene.Field(InputTranslationData,required=True)

class TranslationSuggetion(graphene.Mutation):
    "Mutations for TranslationSuggetion"
    class Arguments:
        """Arguments for TranslationSuggetion"""
        info_arg = InputTranslation()

    data = graphene.List(types.Sentence)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,info_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        sentence_list = info_arg.data.sentacne_list
        source_language = info_arg.source_language
        target_language = info_arg.target_language
        punctuations = info_arg.data.punctuations
        stopwords = info_arg.data.stopwords

        result =nlp_crud.auto_translate(db_=db_,sentence_list=sentence_list,source_lang=\
            source_language,target_lang=target_language,punctuations=punctuations,\
                stop_words=stopwords)

        dict_content_list = []
        for item in result:
            comm = types.Sentence(
            sentenceId = item.sentenceId,
            sentence = item.sentence,
            draft = item.draft,
            draftMeta = item.draftMeta
            )
            dict_content_list.append(comm)
        return TranslationSuggetion(data=dict_content_list)

############### Add Gloss
class InputAddGloss(graphene.InputObjectType):
    """Add Gloss input"""
    source_language = graphene.String(required=True,\
        description="patten:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    target_language  = graphene.String(required=True,\
        description="patten:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    data = graphene.List(types.GlossInput,required=True)

class AddGloss(graphene.Mutation):
    "Mutations for AddGloss"
    class Arguments:
        """Arguments for AddGloss"""
        info_arg = InputAddGloss()

    message = graphene.String()
    data = graphene.List(types.Gloss)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,info_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source_language = info_arg.source_language
        target_language =info_arg.target_language
        schema_list = []
        for item in info_arg.data:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas_nlp.GlossInput)
            schema_list.append(schema_model)

        result =nlp_crud.add_to_translation_memory(db_=db_,src_lang=source_language,\
           trg_lang=target_language,gloss_list=schema_list)

        dict_content_list = []
        for item in result:
            #pylint: disable=R1726
            if "translations" and  "metaData" in item:
                dict_var = types.Gloss(
               token = item["token"],
               translations = item["translations"],
               metaData = item["metaData"]
            )
            elif "translations" in item:
                dict_var = types.Gloss(
               token = item["token"],
               translations = item["translations"]
            )
            elif "metaData" in item:
                dict_var = types.Gloss(
               token = item["token"],
               metaData = item["metaData"]
            )

            dict_content_list.append(dict_var)
        message = "Added to glossary"
        return AddGloss(message=message,data=dict_content_list)

############### Add Alignment
class InputAddAlignment(graphene.InputObjectType):
    """Add Alignement input"""
    source_language = graphene.String(required=True,\
        description="patten:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    target_language  = graphene.String(required=True,\
        description="patten:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    data = graphene.List(types.Alignment,required=True)

class AddAlignment(graphene.Mutation):
    "Mutations for AddAlignment"
    class Arguments:
        """Arguments for AddAlignment"""
        info_arg = InputAddAlignment()

    message = graphene.String()
    data = graphene.List(types.Gloss)
    #pylint: disable=R0201,no-self-use
    def mutate(self,info,info_arg):
        """resolve"""
        db_ = info.context["request"].db_session
        source_language = info_arg.source_language
        target_language =info_arg.target_language
        schema_list = []
        for item in info_arg.data:
            schema_model = utils.convert_graphene_obj_to_pydantic\
            (item,schemas_nlp.Alignment)
            schema_list.append(schema_model)

        result =nlp_crud.alignments_to_trainingdata(db_=db_,src_lang=source_language,\
            trg_lang=target_language,alignment_list=schema_list,user_id=20202)

        dict_content_list = []
        for item in result:
            #pylint: disable=R1726
            if "translations" and  "metaData" in item:
                dict_var = types.Gloss(
               token = item["token"],
               translations = item["translations"],
               metaData = item["metaData"]
            )
            elif "translations" in item:
                dict_var = types.Gloss(
               token = item["token"],
               translations = item["translations"]
            )
            elif "metaData" in item:
                dict_var = types.Gloss(
               token = item["token"],
               metaData = item["metaData"]
            )

            dict_content_list.append(dict_var)
        message = "Added to Alignments"
        return AddAlignment(message=message,data=dict_content_list)

########## ALL MUTATIONS FOR API ########
class VachanMutations(graphene.ObjectType):
    '''All defined mutations'''
    add_language = AddLanguage.Field()
    update_language = UpdateLanguage.Field()
    add_content_type = CreateContentTypes.Field()
    add_license = AddLicense.Field()
    edit_license = EditLicense.Field()
    add_version = AddVersion.Field()
    edit_version = EditVersion.Field()
    add_source = AddSource.Field()
    edit_source = EditSource.Field()
    add_bible_book = AddBible.Field()
    edit_bible_book = EditBible.Field()
    add_audio_bible = AddAudioBible.Field()
    edit_audio_bible = EditAudioBible.Field()
    add_commentary = AddCommentary.Field()
    edit_commentary = EditCommentary.Field()
    add_bible_video = AddBibleVideo.Field()
    edit_bible_video = EditBibleVideo.Field()
    add_dictionary = AddDictionary.Field()
    edit_dictionary = EditDictionary.Field()
    add_infographic = AddInfographic.Field()
    edit_infographic = EditInfographic.Field()
    create_agmt_project = CreateAGMTProject.Field()
    edit_agmt_project = EditAGMTProject.Field()
    create_agmt_project_user = AGMTUserCreate.Field()
    edit_agmt_project_user = AGMTUserEdit.Field()
    apply_token_translation = TokenApply.Field()
    get_token_sentances = GetTokenSentance.Field()
    suggest_auto_translation = AutoTranslationSuggetion.Field()
    suggest_translation = TranslationSuggetion.Field()
    add_gloss = AddGloss.Field()
    add_alignment = AddAlignment.Field()
