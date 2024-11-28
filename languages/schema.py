import graphene
from graphene_django import DjangoObjectType
from .models import Language
from users.schema import UserType
from django.db.models import Q

class LanguageType(DjangoObjectType):
    class Meta:
        model = Language

class Query(graphene.ObjectType):
    languages = graphene.List(LanguageType, search=graphene.String())
    language_by_id = graphene.Field(LanguageType, id_language=graphene.Int())
    
    def resolve_language_by_id(self, info, id_language, **kwargs):
        user = info.context.user 
        
        if user.is_anonymous:
            raise Exception('Not logged in')
        
        print(user)
        
        filter_query = Q(posted_by=user) & Q(id=id_language)
        return Language.objects.filter(filter_query).first()

    def resolve_languages(self, info, search=None, **kwargs):
        user = info.context.user
        
        if user.is_anonymous:
            raise Exception('Not logged in!')
        
        print(user)
        
        if search == "*":
            filter_query = Q(posted_by=user)
            return Language.objects.filter(filter_query)[:10]
        else:
            filter_query = Q(posted_by=user) & Q(name__icontains=search)
            return Language.objects.filter(filter_query)

class CreateLanguage(graphene.Mutation):
    id_language = graphene.Int()
    name = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        name = graphene.String()

    def mutate(self, info, name):
        user = info.context.user or None
        
        if user.is_anonymous:
            raise Exception('Not logged in!')
        
        print(user)

        language = Language(
            name=name,
            posted_by=user
        )

        language.save()

        return CreateLanguage(
            id_language=language.id,
            name=language.name,
            posted_by=language.posted_by
        )

class DeleteLanguage(graphene.Mutation): 
    id_language = graphene.Int() 
    
    class Arguments: 
        id_language = graphene.Int()
    
    def mutate(self, info, id_language): 
        user = info.context.user
        
        if user.is_anonymous: 
            raise Exception('Not logged in!')
        
        print(user)
        
        current_language = Language.objects.filter(id=id_language, posted_by=user).first()
        print(current_language)
        
        if not current_language:
            raise Exception('Invalid Language id!')
        
        current_language.delete()
        
        return DeleteLanguage(
            id_language=id_language,
        )

class Mutation(graphene.ObjectType):
    create_language = CreateLanguage.Field()
    delete_language = DeleteLanguage.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)
