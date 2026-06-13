from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    opengauss_host: str = Field(default="opengauss", alias="OPENGAUSS_HOST")
    opengauss_port: int = Field(default=5432, alias="OPENGAUSS_PORT")
    opengauss_database: str = Field(default="postgres", alias="OPENGAUSS_DATABASE")
    opengauss_user: str = Field(default="gaussdb", alias="OPENGAUSS_USER")
    opengauss_password: str = Field(default="OpenGauss@123", alias="OPENGAUSS_PASSWORD")

    spark_master_url: str = Field(default="spark://spark-master:7077", alias="SPARK_MASTER_URL")
    spark_submit_bin: str = Field(default="/usr/local/bin/spark-submit", alias="SPARK_SUBMIT_BIN")
    spark_jdbc_driver_jar: str = Field(default="/opt/jdbc/opengauss-jdbc.jar", alias="SPARK_JDBC_DRIVER_JAR")
    spark_jdbc_driver_class: str = Field(default="org.postgresql.Driver", alias="SPARK_JDBC_DRIVER_CLASS")
    spark_submit_timeout_seconds: int = Field(default=240, alias="SPARK_SUBMIT_TIMEOUT_SECONDS")

    @property
    def database_url(self) -> str:
        return URL.create(
            "postgresql+psycopg",
            username=self.opengauss_user,
            password=self.opengauss_password,
            host=self.opengauss_host,
            port=self.opengauss_port,
            database=self.opengauss_database,
        ).render_as_string(hide_password=False)

    @property
    def jdbc_url(self) -> str:
        return f"jdbc:opengauss://{self.opengauss_host}:{self.opengauss_port}/{self.opengauss_database}"

    @property
    def spark_jdbc_url(self) -> str:
        return f"jdbc:postgresql://{self.opengauss_host}:{self.opengauss_port}/{self.opengauss_database}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
