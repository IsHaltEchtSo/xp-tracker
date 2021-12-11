from flask import Blueprint, render_template, url_for, request, redirect, url_for, session
from .forms import SessionForm, SkillForm
import json
from datetime import date


skill_bp = Blueprint(
    'skill_bp', __name__, url_prefix='/skills', template_folder='templates'
)


from .errorhandlers import *
from .helper_functions import (
     load_skills_from, dump_skills_to, load_xp_rewards, calculate_lv
)


@skill_bp.route('/', methods=['POST', 'GET'])
@skill_bp.route('/overview', methods=['POST', 'GET'])
def index():
    form = SkillForm(request.form)
    skills = load_skills_from(path='json/skills.json')
    skill_sessions = []

    for skill_name, skill_props in skills.items():
        for skill_session in skill_props['sessions']:
            skill_sessions.append(skill_session)

    if request.method == 'POST' and form.validate():
        new_skill_name = form.skill_name.data
        new_skill = {'name':new_skill_name, 'xp':0, 'lv':'1', 'sessions':[]}
        skills[new_skill_name] = new_skill
        dump_skills_to(path='json/skills.json', skills=skills)
        return redirect(url_for('skill_bp.index'))

    return render_template('index.html',
        form=form,
        skills=skills,
        skill_sessions=skill_sessions
    )



@skill_bp.route('/<skill_name>', methods=['POST', 'GET'])
def skill_page(skill_name):
    form = SessionForm(request.form)
    skills = load_skills_from(path='json/skills.json')
    skill = skills[skill_name]
    skill_sessions = skill['sessions']

    if request.method == 'POST' and form.validate():
        xp_rewards = load_xp_rewards()
        new_session = {
             'date':str(date.today()),
             'xp':0,
             'mediums':[]
        }
        populated_medium_fields = {}

        for field in form:
            if field.widget.input_type != 'hidden':
                if field.name != 'topic' and field.data:
                    populated_medium_fields[field.name] = field.data
                elif field.name == 'topic':
                    new_session['topic'] = field.data

        for medium_name, medium_value in populated_medium_fields.items():
            xp = xp_rewards[medium_name] * medium_value

            new_medium = {
                'medium': medium_name,
                'amount': medium_value,
                'xp':xp
            }

            new_session['xp'] += xp
            new_session['mediums'].append(new_medium)


        skill_sessions.append(new_session)
        skill['sessions'] = skill_sessions
        skill['xp'] += new_session['xp']
        skill['lv'] = calculate_lv(skill['xp'])

        dump_skills_to(path='json/skills.json', skills=skills)
        return redirect(url_for('skill_bp.reward_page', skill=skill_name))

    return render_template('skill.html',
        skill=skill,
        skill_name=skill_name,
        skill_sessions=skill_sessions,
        form=form
    )



@skill_bp.route('/<skill>/reward')
def reward_page(skill):
    return render_template('reward.html', skill=skill)
