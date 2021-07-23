'''GraphQL queries and mutations'''
import graphene

#pylint: disable=E0401
#pylint gives import error if relative import is not used. But app(uvicorn) doesn't accept it
from crud import structurals_crud,contents_crud
#pylint: disable=E0611
from graphql_api import types, utils
import schemas

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
