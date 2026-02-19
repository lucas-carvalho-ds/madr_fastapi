from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]


@table_registry.mapped_as_dataclass
class Romancista:
    __tablename__ = 'romancistas'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]

    livros: Mapped[list['Livro']] = relationship(
        init=False,
        back_populates='romancista',
        cascade='all, delete-orphan', 
        lazy='selectin'
    )


@table_registry.mapped_as_dataclass
class Livro:
    __tablename__ = 'livros'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    year: Mapped[int]
    novelist_id: Mapped[int] = mapped_column(ForeignKey('romancistas.id'))

    romancista: Mapped[Romancista] = relationship(
        init=False, back_populates='livros'
    )




