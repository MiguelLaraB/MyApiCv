import graphene
from graphene_django import DjangoObjectType
from .models import Skill
from users.schema import UserType
from django.db.models import Q

class SkillType(DjangoObjectType):
    class Meta:
        model = Skill

class Query(graphene.ObjectType):
    skills = graphene.List(SkillType, search=graphene.String())
    skillById = graphene.Field(SkillType, id_skill=graphene.Int())
    
    def resolve_skillById(self, info, id_skill, **kwargs):
        user = info.context.user 
        
        if user.is_anonymous:
            raise Exception('Not logged in')
        
        print(user)
        
        filter = (
            Q(posted_by=user) & Q(id=id_skill)
        )
        
        return Skill.objects.filter(filter).first()

    def resolve_skills(self, info, search=None, **kwargs):
        user = info.context.user
        
        if user.is_anonymous:
            raise Exception('Not logged in!')
        
        print(user)
        
        if search == "*":
            filter = Q(posted_by=user)
            return Skill.objects.filter(filter)[:10]
        else:
            filter = Q(posted_by=user) & Q(skill__icontains=search)
            return Skill.objects.filter(filter)

class CreateSkill(graphene.Mutation):
    id_skill = graphene.Int()
    skill = graphene.String()
    level = graphene.Int()
    posted_by = graphene.Field(UserType)

    class Arguments:
        skill = graphene.String()
        level = graphene.Int()

    def mutate(self, info, skill, level):
        user = info.context.user
        
        if user.is_anonymous:
            raise Exception('Not logged in!')
        
        print(user)

        skill_instance = Skill(
            skill=skill,
            level=level,
            posted_by=user
        )

        skill_instance.save()

        return CreateSkill(
            id_skill=skill_instance.id,
            skill=skill_instance.skill,
            level=skill_instance.level,
            posted_by=skill_instance.posted_by
        )

class DeleteSkill(graphene.Mutation): 
    id_skill = graphene.Int() 
    
    class Arguments: 
        id_skill = graphene.Int()
    
    def mutate(self, info, id_skill): 
        user = info.context.user
        
        if user.is_anonymous: 
            raise Exception('Not logged in!')
        
        print(user) 
        
        current_skill = Skill.objects.filter(id=id_skill, posted_by=user).first()
        print(current_skill)
        
        if not current_skill:
            raise Exception('Invalid Skill id!')
        
        current_skill.delete()
        
        return DeleteSkill(
            id_skill=id_skill,
        )

class Mutation(graphene.ObjectType):
    create_skill = CreateSkill.Field()
    delete_skill = DeleteSkill.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)
