"""initial_database_schema

Revision ID: 87db6a21b127
Revises: 
Create Date: 2026-09-07 23:32:04.869565

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87db6a21b127'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('preferred_language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. institutions
    op.create_table(
        'institutions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('institution_type', sa.String(length=100), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('verification_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_institutions_name'), 'institutions', ['name'], unique=False)
    op.create_index(op.f('ix_institutions_district'), 'institutions', ['district'], unique=False)

    # 3. institution_expertise
    op.create_table(
        'institution_expertise',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=False),
        sa.Column('domain', sa.String(length=100), nullable=False),
        sa.Column('subdomain', sa.String(length=100), nullable=True),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('expertise_level', sa.String(length=50), nullable=True),
        sa.Column('facilities', sa.Text(), nullable=True),
        sa.Column('research_areas', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_institution_expertise_institution_id'), 'institution_expertise', ['institution_id'], unique=False)
    op.create_index(op.f('ix_institution_expertise_domain'), 'institution_expertise', ['domain'], unique=False)

    # 4. challenges
    op.create_table(
        'challenges',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('submitted_by', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='submitted'),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('priority_score', sa.Float(), nullable=True),
        sa.Column('people_affected', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['submitted_by'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_challenges_title'), 'challenges', ['title'], unique=False)
    op.create_index(op.f('ix_challenges_submitted_by'), 'challenges', ['submitted_by'], unique=False)
    op.create_index(op.f('ix_challenges_status'), 'challenges', ['status'], unique=False)
    op.create_index(op.f('ix_challenges_category'), 'challenges', ['category'], unique=False)

    # 5. challenge_locations
    op.create_table(
        'challenge_locations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False, server_default='Jharkhand'),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('block', sa.String(length=100), nullable=True),
        sa.Column('panchayat', sa.String(length=100), nullable=True),
        sa.Column('village', sa.String(length=100), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.CheckConstraint("state = 'Jharkhand'", name='ck_challenge_location_jharkhand_only'),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_challenge_locations_challenge_id'), 'challenge_locations', ['challenge_id'], unique=True)
    op.create_index(op.f('ix_challenge_locations_district'), 'challenge_locations', ['district'], unique=False)

    # 6. challenge_evidence
    op.create_table(
        'challenge_evidence',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_challenge_evidence_challenge_id'), 'challenge_evidence', ['challenge_id'], unique=False)

    # 7. challenge_ai_analysis
    op.create_table(
        'challenge_ai_analysis',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('priority_score', sa.Float(), nullable=True),
        sa.Column('duplicate_score', sa.Float(), nullable=True),
        sa.Column('required_expertise', sa.Text(), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_challenge_ai_analysis_challenge_id'), 'challenge_ai_analysis', ['challenge_id'], unique=True)

    # 8. challenge_assignments
    op.create_table(
        'challenge_assignments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=False),
        sa.Column('match_score', sa.Float(), nullable=True),
        sa.Column('match_reason', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='proposed'),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_challenge_assignments_challenge_id'), 'challenge_assignments', ['challenge_id'], unique=False)
    op.create_index(op.f('ix_challenge_assignments_institution_id'), 'challenge_assignments', ['institution_id'], unique=False)

    # 9. projects
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='planning'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('target_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_projects_challenge_id'), 'projects', ['challenge_id'], unique=False)
    op.create_index(op.f('ix_projects_institution_id'), 'projects', ['institution_id'], unique=False)
    op.create_index(op.f('ix_projects_status'), 'projects', ['status'], unique=False)

    # 10. project_members
    op.create_table(
        'project_members',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_project_members_project_id'), 'project_members', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_members_user_id'), 'project_members', ['user_id'], unique=False)

    # 11. industry_partners
    op.create_table(
        'industry_partners',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('partner_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('expertise', sa.Text(), nullable=True),
        sa.Column('verification_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_industry_partners_name'), 'industry_partners', ['name'], unique=False)

    # 12. project_collaborations
    op.create_table(
        'project_collaborations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('partner_id', sa.Integer(), nullable=False),
        sa.Column('collaboration_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['partner_id'], ['industry_partners.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_project_collaborations_project_id'), 'project_collaborations', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_collaborations_partner_id'), 'project_collaborations', ['partner_id'], unique=False)

    # 13. milestones
    op.create_table(
        'milestones',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_milestones_project_id'), 'milestones', ['project_id'], unique=False)

    # 14. impact_metrics
    op.create_table(
        'impact_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_impact_metrics_project_id'), 'impact_metrics', ['project_id'], unique=False)

    # 15. notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('impact_metrics')
    op.drop_table('milestones')
    op.drop_table('project_collaborations')
    op.drop_table('industry_partners')
    op.drop_table('project_members')
    op.drop_table('projects')
    op.drop_table('challenge_assignments')
    op.drop_table('challenge_ai_analysis')
    op.drop_table('challenge_evidence')
    op.drop_table('challenge_locations')
    op.drop_table('challenges')
    op.drop_table('institution_expertise')
    op.drop_table('institutions')
    op.drop_table('users')
