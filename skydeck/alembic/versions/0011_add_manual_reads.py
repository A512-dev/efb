# TODO: id bigint identity primary key
# org_id bigint not null references orgs(id) on delete cascade
# user_id bigint not null references users(id) on delete cascade
# manual_id bigint not null references manuals(id) on delete cascade
# read_at timestamptz default now()
# last_read_at timestamptz default now()
# read_count integer default 1
# created_at timestamptz default now()
# unique(user_id, manual_id)