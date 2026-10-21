resource "aiven_pg" "analytics" {
  project      = var.aiven_project
  service_name = var.service_name
  plan         = var.aiven_plan
  cloud_name   = var.aiven_cloud_name

  termination_protection = var.termination_protection

  pg_user_config {
    service_log = true

    public_access {
      pg         = var.enable_public_access
      prometheus = false
    }
  }

  tag {
    key   = "project"
    value = "equityscope"
  }

  tag {
    key   = "purpose"
    value = "analytics"
  }

  timeouts {
    create = "30m"
    update = "30m"
    delete = "30m"
  }
}

resource "aiven_pg_database" "analytics" {
  project       = var.aiven_project
  service_name  = aiven_pg.analytics.service_name
  database_name = var.database_name

  lifecycle {
    prevent_destroy = true
  }
}
