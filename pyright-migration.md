/Users/james/Documents/GitHub/panoptikon/scripts/benchmark_pool.py
  /Users/james/Documents/GitHub/panoptikon/scripts/benchmark_pool.py:155:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/benchmark_pool.py:157:24 - error: Argument type is partially unknown
    Argument corresponds to parameter "results" in function "write_markdown"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/benchmark_pool.py:163:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/benchmark_pool.py:165:24 - error: Argument type is partially unknown
    Argument corresponds to parameter "results" in function "write_markdown"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
/Users/james/Documents/GitHub/panoptikon/scripts/documentation/ai_docs.py
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/ai_docs.py:90:44 - error: Argument of type "str | bool | Any" cannot be assigned to parameter "handler" of type "BaseHandler | None" in function "__init__"
    Type "str | bool | Any" is not assignable to type "BaseHandler | None"
      Type "bool" is not assignable to type "BaseHandler | None"
        "bool" is not assignable to "BaseHandler"
        "bool" is not assignable to "None" (reportArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/ai_docs.py:114:9 - error: Type of "query_vector" is partially unknown
    Type of "query_vector" is "list[Unknown]" (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/ai_docs.py:114:24 - error: Type of "encode" is partially unknown
    Type of "encode" is "Overload[(sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding', 'token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: Literal[False] = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor, (sentences: str | list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: Literal[True] = ..., convert_to_tensor: Literal[False] = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> ndarray[Unknown, Unknown], (sentences: str | list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: Literal[True] = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor, (sentences: list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding', 'token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> list[Tensor], (sentences: list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: None = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> list[dict[str, Tensor]], (sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: None = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> dict[str, Tensor], (sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/ai_docs.py:114:24 - error: Type of "tolist" is partially unknown
    Type of "tolist" is "() -> list[Unknown]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/ai_docs.py:116:56 - error: Argument type is partially unknown
    Argument corresponds to parameter "query_vector" in function "search"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/ai_docs.py:136:9 - error: Type of "embedding" is partially unknown
    Type of "embedding" is "list[Unknown]" (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/ai_docs.py:136:21 - error: Type of "encode" is partially unknown
    Type of "encode" is "Overload[(sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding', 'token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: Literal[False] = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor, (sentences: str | list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: Literal[True] = ..., convert_to_tensor: Literal[False] = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> ndarray[Unknown, Unknown], (sentences: str | list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: Literal[True] = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor, (sentences: list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding', 'token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> list[Tensor], (sentences: list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: None = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> list[dict[str, Tensor]], (sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: None = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> dict[str, Tensor], (sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/ai_docs.py:136:21 - error: Type of "tolist" is partially unknown
    Type of "tolist" is "() -> list[Unknown]" (reportUnknownMemberType)
/Users/james/Documents/GitHub/panoptikon/scripts/documentation/dual_reindex.py
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/dual_reindex.py:70:13 - error: Type of "embedding" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/dual_reindex.py:70:25 - error: Type of "encode" is partially unknown
    Type of "encode" is "Overload[(sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding', 'token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: Literal[False] = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor, (sentences: str | list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: Literal[True] = ..., convert_to_tensor: Literal[False] = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> ndarray[Unknown, Unknown], (sentences: str | list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: Literal[True] = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor, (sentences: list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding', 'token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> list[Tensor], (sentences: list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: None = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> list[dict[str, Tensor]], (sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: None = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> dict[str, Tensor], (sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/dual_reindex.py:74:50 - error: Type of "tolist" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/dual_reindex.py:134:33 - error: Argument of type "Path" cannot be assigned to parameter "fd" of type "str | IOBase" in function "load"
    Type "Path" is not assignable to type "str | IOBase"
      "Path" is not assignable to "str"
      "Path" is not assignable to "IOBase" (reportArgumentType)
/Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py:18:39 - error: Type of "MKDocsToQdrant" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py:21:5 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py:63:31 - error: Argument of type "str | list[str]" cannot be assigned to parameter "name" of type "str" in function "document_phase"
    Type "str | list[str]" is not assignable to type "str"
      "list[str]" is not assignable to "str" (reportArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py:64:9 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py:88:9 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py:105:9 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py:108:31 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py:109:12 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py:118:5 - error: Type of "indexer" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py:126:5 - error: Type of "run" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py:156:5 - error: Type of "created_files" is partially unknown
    Type of "created_files" is "list[Unknown]" (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_complete.py:165:28 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
/Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_kg_to_docs.py
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_kg_to_docs.py:23:5 - error: Type of "document_phase" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_kg_to_docs.py:23:10 - error: Cannot access attribute "document_phase" for class "AIDocumentationSystem"
    Attribute "document_phase" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_kg_to_docs.py:42:5 - error: Type of "record_decision" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_kg_to_docs.py:42:10 - error: Cannot access attribute "record_decision" for class "AIDocumentationSystem"
    Attribute "record_decision" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_kg_to_docs.py:52:5 - error: Type of "document_component" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/migrate_kg_to_docs.py:52:10 - error: Cannot access attribute "document_component" for class "AIDocumentationSystem"
    Attribute "document_component" is unknown (reportAttributeAccessIssue)
/Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:37:24 - error: Type of parameter "metadata" is partially unknown
    Parameter type is "Dict[Unknown, Unknown]" (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:37:34 - error: Expected type arguments for generic class "Dict" (reportMissingTypeArgument)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:37:41 - error: Expression of type "None" cannot be assigned to parameter of type "Dict[Unknown, Unknown]"
    "None" is not assignable to "Dict[Unknown, Unknown]" (reportArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:44:9 - error: Type of "meta" is partially unknown
    Type of "meta" is "dict[str | Unknown, str | bool | Unknown]" (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:54:44 - error: Argument type is partially unknown
    Argument corresponds to parameter "metadata" in function "__init__"
    Argument type is "str | bool | Unknown" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:54:44 - error: Argument of type "str | bool | Unknown" cannot be assigned to parameter "handler" of type "BaseHandler | None" in function "__init__"
    Type "str | bool | Unknown" is not assignable to type "BaseHandler | None"
      Type "bool" is not assignable to type "BaseHandler | None"
        "bool" is not assignable to "BaseHandler"
        "bool" is not assignable to "None" (reportArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:63:57 - error: Type of parameter "details" is partially unknown
    Parameter type is "Dict[Unknown, Unknown]" (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:63:66 - error: Expected type arguments for generic class "Dict" (reportMissingTypeArgument)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:68:2 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:71:2 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:74:2 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:77:2 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:80:20 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:81:19 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:85:16 - error: Type of "create_document" is partially unknown
    Type of "create_document" is "(category: str, title: str, content: str, metadata: Dict[Unknown, Unknown] = None) -> Path" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:90:35 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:91:26 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:95:49 - error: Type of parameter "details" is partially unknown
    Parameter type is "Dict[Unknown, Unknown]" (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:95:58 - error: Expected type arguments for generic class "Dict" (reportMissingTypeArgument)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:100:2 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:103:2 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:106:2 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:109:2 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:112:2 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:115:2 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:118:16 - error: Type of "create_document" is partially unknown
    Type of "create_document" is "(category: str, title: str, content: str, metadata: Dict[Unknown, Unknown] = None) -> Path" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:123:33 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:124:27 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:136:5 - error: Type of "create_phase_doc" is partially unknown
    Type of "create_phase_doc" is "(phase_name: str, details: Dict[Unknown, Unknown]) -> Path" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/documentation/simple_migrate.py:157:5 - error: Type of "create_component_doc" is partially unknown
    Type of "create_component_doc" is "(component_name: str, details: Dict[Unknown, Unknown]) -> Path" (reportUnknownMemberType)
/Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py
  /Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py:50:9 - error: Type of "embedding" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py:50:21 - error: Type of "encode" is partially unknown
    Type of "encode" is "Overload[(sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding', 'token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: Literal[False] = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor, (sentences: str | list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: Literal[True] = ..., convert_to_tensor: Literal[False] = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> ndarray[Unknown, Unknown], (sentences: str | list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: Literal[True] = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor, (sentences: list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding', 'token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> list[Tensor], (sentences: list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: None = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> list[dict[str, Tensor]], (sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: None = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> dict[str, Tensor], (sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py:54:46 - error: Type of "tolist" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py:68:9 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py:69:16 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py:70:67 - error: Argument type is partially unknown
    Argument corresponds to parameter "points" in function "upsert"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py:71:34 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py:74:63 - error: Argument type is partially unknown
    Argument corresponds to parameter "points" in function "upsert"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py:75:30 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py:96:9 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py:100:27 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/dual_reindex.py:105:29 - error: Argument of type "Path" cannot be assigned to parameter "fd" of type "str | IOBase" in function "load"
    Type "Path" is not assignable to type "str | IOBase"
      "Path" is not assignable to "str"
      "Path" is not assignable to "IOBase" (reportArgumentType)
/Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:39:9 - error: Type of "extend" is partially unknown
    Type of "extend" is "(iterable: Iterable[Unknown], /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:43:12 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:50:29 - error: Argument of type "Path" cannot be assigned to parameter "fd" of type "str | IOBase" in function "load"
    Type "Path" is not assignable to type "str | IOBase"
      "Path" is not assignable to "str"
      "Path" is not assignable to "IOBase" (reportArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:109:5 - error: Type of "unresolved_ids" is partially unknown
    Type of "unresolved_ids" is "set[Unknown]" (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:116:17 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:118:17 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:119:17 - error: Type of "add" is partially unknown
    Type of "add" is "(element: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:121:29 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:123:31 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:124:13 - error: Type of "batch" is partially unknown
    Type of "batch" is "list[Unknown]" (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:125:67 - error: Argument type is partially unknown
    Argument corresponds to parameter "points" in function "upsert"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:126:28 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:131:13 - error: Type of "path" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:134:35 - error: Argument type is partially unknown
    Argument corresponds to parameter "ids" in function "delete_points"
    Argument type is "set[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/audit_fix_metadata.py:144:43 - error: Argument type is partially unknown
    Argument corresponds to parameter "ids" in function "delete_points"
    Argument type is "set[Unknown]" (reportUnknownArgumentType)
/Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:29:5 - error: Type of "extend" is partially unknown
    Type of "extend" is "(iterable: Iterable[Unknown], /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:35:20 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:41:5 - error: Type of "point" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:41:19 - error: Argument type is partially unknown
    Argument corresponds to parameter "iterable" in function "__init__"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:42:5 - error: Type of "payload" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:42:15 - error: Type of "payload" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:49:5 - error: Type of "vector" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:49:14 - error: Type of "vector" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:50:16 - error: Argument type is unknown
    Argument corresponds to parameter "obj" in function "hasattr" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:52:9 - error: Type of "vector" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:52:18 - error: Type of "get" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:55:12 - error: Type of "id" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:55:12 - error: Argument type is unknown
    Argument corresponds to parameter "id" in function "__init__" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:56:16 - error: Argument type is partially unknown
    Argument corresponds to parameter "vector" in function "__init__"
    Argument type is "dict[str, List[float] | SparseVector | List[List[float]] | Document | Image | InferenceObject] | Unknown" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:57:17 - error: Argument type is unknown
    Argument corresponds to parameter "payload" in function "__init__" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:59:5 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:64:28 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:65:5 - error: Type of "batch" is partially unknown
    Type of "batch" is "list[Unknown]" (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:68:16 - error: Argument type is partially unknown
    Argument corresponds to parameter "points" in function "upsert"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/fix_document_field.py:71:37 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
/Users/james/Documents/GitHub/panoptikon/scripts/qdrant/test_mcp.py
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/test_mcp.py:42:21 - error: Type of "encode" is partially unknown
    Type of "encode" is "Overload[(sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding', 'token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: Literal[False] = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor, (sentences: str | list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: Literal[True] = ..., convert_to_tensor: Literal[False] = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> ndarray[Unknown, Unknown], (sentences: str | list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: Literal[True] = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor, (sentences: list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['sentence_embedding', 'token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> list[Tensor], (sentences: list[str] | ndarray[Unknown, Unknown], prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: None = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> list[dict[str, Tensor]], (sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: None = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> dict[str, Tensor], (sentences: str, prompt_name: str | None = ..., prompt: str | None = ..., batch_size: int = ..., show_progress_bar: bool | None = ..., output_value: Literal['token_embeddings'] = ..., precision: Literal['float32', 'int8', 'uint8', 'binary', 'ubinary'] = ..., convert_to_numpy: bool = ..., convert_to_tensor: bool = ..., device: str | None = ..., normalize_embeddings: bool = ..., **kwargs: Unknown) -> Tensor]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/test_mcp.py:48:30 - error: Argument type is partially unknown
    Argument corresponds to parameter "query_vector" in function "search"
    Argument type is "tuple[Literal['fast-all-minilm-l6-v2'], list[Unknown]]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/test_mcp.py:48:56 - error: Type of "tolist" is partially unknown
    Type of "tolist" is "() -> list[Unknown]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/test_mcp.py:56:56 - error: "get" is not a known attribute of "None" (reportOptionalMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/test_mcp.py:57:55 - error: "get" is not a known attribute of "None" (reportOptionalMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/scripts/qdrant/test_mcp.py:58:58 - error: "get" is not a known attribute of "None" (reportOptionalMemberAccess)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/config.py
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/config.py:329:13 - error: Type of "update" is partially unknown
    Type of "update" is "Overload[(m: SupportsKeysAndGetItem[Unknown, Unknown], /, **kwargs: Unknown) -> None, (m: Iterable[tuple[Unknown, Unknown]], /, **kwargs: Unknown) -> None, (**kwargs: Unknown) -> None]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/config.py:333:13 - error: Type of "update" is partially unknown
    Type of "update" is "Overload[(m: SupportsKeysAndGetItem[Unknown, Unknown], /, **kwargs: Unknown) -> None, (m: Iterable[tuple[Unknown, Unknown]], /, **kwargs: Unknown) -> None, (**kwargs: Unknown) -> None]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/config.py:337:13 - error: Type of "update" is partially unknown
    Type of "update" is "Overload[(m: SupportsKeysAndGetItem[Unknown, Unknown], /, **kwargs: Unknown) -> None, (m: Iterable[tuple[Unknown, Unknown]], /, **kwargs: Unknown) -> None, (**kwargs: Unknown) -> None]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/config.py:339:16 - error: Return type, "dict[Unknown, Unknown]", is partially unknown (reportUnknownVariableType)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/errors.py
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/errors.py:56:5 - error: Type of "environment" is partially unknown
    Type of "environment" is "dict[Unknown, Unknown]" (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/errors.py:57:5 - error: Type of "related_objects" is partially unknown
    Type of "related_objects" is "dict[Unknown, Unknown]" (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/errors.py:459:9 - warning: Variable "exc_type" is not accessed (reportUnusedVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/errors.py:459:19 - warning: Variable "exc_value" is not accessed (reportUnusedVariable)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/events.py
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/events.py:268:34 - error: Unnecessary isinstance call; "EventHandler[T@subscribe] | AsyncEventHandler[T@subscribe]" is always an instance of "EventHandler[Unknown] | AsyncEventHandler[Unknown]" (reportUnnecessaryIsInstance)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/events.py:287:21 - error: Argument of type "AsyncEventHandler[Unknown] | AsyncEventHandler[T@subscribe] | ((T@subscribe) -> Coroutine[Any, Any, Any]) | EventHandler[T@subscribe] | ((T@subscribe) -> None) | ((T@subscribe) -> Future[None])" cannot be assigned to parameter "handler" of type "EventHandler[Any] | AsyncEventHandler[Any] | ((Any) -> None) | ((Any) -> Future[None])" in function "__init__"
    Type "AsyncEventHandler[Unknown] | AsyncEventHandler[T@subscribe] | ((T@subscribe) -> Coroutine[Any, Any, Any]) | EventHandler[T@subscribe] | ((T@subscribe) -> None) | ((T@subscribe) -> Future[None])" is not assignable to type "EventHandler[Any] | AsyncEventHandler[Any] | ((Any) -> None) | ((Any) -> Future[None])"
      Type "(T@subscribe) -> Coroutine[Any, Any, Any]" is not assignable to type "EventHandler[Any] | AsyncEventHandler[Any] | ((Any) -> None) | ((Any) -> Future[None])"
        "function" is not assignable to "EventHandler[Any]"
        "function" is not assignable to "AsyncEventHandler[Any]"
        Type "(T@subscribe) -> Coroutine[Any, Any, Any]" is not assignable to type "(Any) -> None"
          Function return type "Coroutine[Any, Any, Any]" is incompatible with type "None"
            "Coroutine[Any, Any, Any]" is not assignable to "None"
        Type "(T@subscribe) -> Coroutine[Any, Any, Any]" is not assignable to type "(Any) -> Future[None]"
    ... (reportArgumentType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/events.py:433:28 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "hasattr"
    Argument type is "EventHandler[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/events.py:433:63 - error: Type of "handle" is partially unknown
    Type of "handle" is "(event: Unknown) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/events.py:433:63 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "callable"
    Argument type is "(event: Unknown) -> None" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/events.py:435:13 - error: Type of "handle" is partially unknown
    Type of "handle" is "(event: Unknown) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/events.py:457:28 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "hasattr"
    Argument type is "AsyncEventHandler[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/events.py:457:63 - error: Type of "handle" is partially unknown
    Type of "handle" is "(event: Unknown) -> CoroutineType[Any, Any, None]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/events.py:457:63 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "callable"
    Argument type is "(event: Unknown) -> CoroutineType[Any, Any, None]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/events.py:459:46 - error: Type of "handle" is partially unknown
    Type of "handle" is "(event: Unknown) -> CoroutineType[Any, Any, None]" (reportUnknownMemberType)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/service.py
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/service.py:263:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/service.py:265:9 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/core/service.py:266:28 - error: Argument type is partially unknown
    Argument corresponds to parameter "iterable" in function "join"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/pool.py
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/pool.py:335:42 - error: "conn_obj" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/pool.py:438:42 - error: "conn_obj" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/pool.py:790:21 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/pool.py:796:21 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/pool.py:802:17 - error: Type of "conn" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/pool.py:804:51 - error: Argument type is unknown
    Argument corresponds to parameter "value" in function "remove" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/pool.py:805:44 - error: Argument type is unknown
    Argument corresponds to parameter "pooled_conn" in function "_close_connection" (reportUnknownArgumentType)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/query_builder.py
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/query_builder.py:48:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/query_builder.py:50:37 - error: Argument type is partially unknown
    Argument corresponds to parameter "iterable" in function "join"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/query_builder.py:51:16 - error: Return type, "tuple[LiteralString, dict[Unknown, Unknown]]", is partially unknown (reportUnknownVariableType)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/schema.py
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/schema.py:472:21 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/database/schema.py:480:16 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownVariableType)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:29:9 - error: "MACOS_APIS_AVAILABLE" is constant (because it is uppercase) and cannot be redefined (reportConstantRedefinition)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:31:5 - error: "MACOS_APIS_AVAILABLE" is constant (because it is uppercase) and cannot be redefined (reportConstantRedefinition)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:102:19 - error: "Foundation" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:103:13 - error: Type of "bookmark_data" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:103:28 - error: Type of "error" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:104:17 - error: Type of "bookmarkDataWithOptions_includingResourceValuesForKeys_relativeToURL_error_" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:104:21 - error: Cannot access attribute "bookmarkDataWithOptions_includingResourceValuesForKeys_relativeToURL_error_" for class "NSURL"
    Attribute "bookmarkDataWithOptions_includingResourceValuesForKeys_relativeToURL_error_" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:105:21 - error: Type of "NSURLBookmarkCreationWithSecurityScope" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:105:21 - error: "Foundation" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:105:32 - error: "NSURLBookmarkCreationWithSecurityScope" is not a known attribute of module "Foundation" (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:113:17 - error: Type of "error_info" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:113:30 - error: Type of "localizedDescription" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:117:74 - error: Argument type is unknown
    Argument corresponds to parameter "object" in function "__new__" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:126:37 - error: Argument type is unknown
    Argument corresponds to parameter "o" in function "__new__" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:171:13 - error: Type of "url" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:171:19 - error: Type of "URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:171:19 - error: "Foundation" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:171:36 - error: Cannot access attribute "URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_" for class "type[NSURL]"
    Attribute "URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:172:17 - error: Type of "NSData" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:172:17 - error: Type of "dataWithBytes_length_" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:172:17 - error: "Foundation" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:172:28 - error: "NSData" is not a known attribute of module "Foundation" (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:176:17 - error: Type of "NSURLBookmarkResolutionWithSecurityScope" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:176:17 - error: "Foundation" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:176:28 - error: "NSURLBookmarkResolutionWithSecurityScope" is not a known attribute of module "Foundation" (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:178:17 - error: Type of "NULL" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:178:17 - error: "objc" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:178:22 - error: "NULL" is not a known attribute of module "objc" (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:193:13 - error: Type of "success" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:193:23 - error: Type of "startAccessingSecurityScopedResource" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:238:19 - error: "Foundation" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:239:13 - error: Type of "stopAccessingSecurityScopedResource" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:239:17 - error: Cannot access attribute "stopAccessingSecurityScopedResource" for class "NSURL"
    Attribute "stopAccessingSecurityScopedResource" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:423:13 - error: Type of "url" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:423:18 - error: Type of "is_stale" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:423:28 - error: Type of "error" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:424:17 - error: Type of "URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:424:17 - error: "Foundation" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:424:34 - error: Cannot access attribute "URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_" for class "type[NSURL]"
    Attribute "URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:425:21 - error: Type of "NSData" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:425:21 - error: Type of "dataWithBytes_length_" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:425:21 - error: "Foundation" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:425:32 - error: "NSData" is not a known attribute of module "Foundation" (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:428:21 - error: Type of "NSURLBookmarkResolutionWithSecurityScope" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:428:21 - error: "Foundation" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:428:32 - error: "NSURLBookmarkResolutionWithSecurityScope" is not a known attribute of module "Foundation" (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/bookmarks.py:438:24 - error: Type of "localizedDescription" is unknown (reportUnknownMemberType)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/cloud.py
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/cloud.py:247:17 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/cloud.py:249:16 - error: Return type, "list[Unknown]", is partially unknown (reportUnknownVariableType)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:24:5 - error: "FSEVENTS_AVAILABLE" is constant (because it is uppercase) and cannot be redefined (reportConstantRedefinition)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:111:34 - error: "Observer" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:112:35 - error: "Stream" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:120:26 - error: "Observer" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:121:9 - error: Type of "_observer" is partially unknown
    Type of "_observer" is "Unknown | None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:121:9 - error: Type of "start" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:121:24 - error: "start" is not a known attribute of "None" (reportOptionalMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:125:20 - error: Type of "stream" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:125:30 - error: Type of "_streams" is partially unknown
    Type of "_streams" is "dict[Path, Unknown | Unbound]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:126:13 - error: Type of "_observer" is partially unknown
    Type of "_observer" is "Unknown | None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:126:13 - error: Type of "schedule" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:126:28 - error: "schedule" is not a known attribute of "None" (reportOptionalMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:132:38 - error: Type of "_observer" is partially unknown
    Type of "_observer" is "Unknown | None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:135:9 - error: Type of "_observer" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:135:9 - error: Type of "stop" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:136:9 - error: Type of "_observer" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:136:9 - error: Type of "join" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:153:20 - error: Type of "_streams" is partially unknown
    Type of "_streams" is "dict[Path, Unknown | Unbound]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:179:9 - error: Type of "stream" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:179:18 - error: "Stream" is possibly unbound (reportPossiblyUnboundVariable)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:180:9 - error: Type of "_streams" is partially unknown
    Type of "_streams" is "dict[Path, Unknown | Unbound]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:183:31 - error: Type of "_observer" is partially unknown
    Type of "_observer" is "Unknown | None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:184:13 - error: Type of "_observer" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:184:13 - error: Type of "schedule" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:194:24 - error: Type of "_streams" is partially unknown
    Type of "_streams" is "dict[Path, Unknown | Unbound]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:198:9 - error: Type of "stream" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:198:18 - error: Type of "_streams" is partially unknown
    Type of "_streams" is "dict[Path, Unknown | Unbound]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:198:18 - error: Type of "pop" is partially unknown
    Type of "pop" is "Overload[(key: Path, /) -> (Unknown | Unbound), (key: Path, default: Unknown | Unbound, /) -> (Unknown | Unbound), (key: Path, default: _T@pop, /) -> (Unknown | Unbound | _T@pop)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:199:31 - error: Type of "_observer" is partially unknown
    Type of "_observer" is "Unknown | None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:200:13 - error: Type of "_observer" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:200:13 - error: Type of "unschedule" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:213:24 - error: Type of "_streams" is partially unknown
    Type of "_streams" is "dict[Path, Unknown | Unbound]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:221:20 - error: Type of "_streams" is partially unknown
    Type of "_streams" is "dict[Path, Unknown | Unbound]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/filesystem/watcher.py:221:20 - error: Argument type is partially unknown
    Argument corresponds to parameter "iterable" in function "__init__"
    Argument type is "dict_keys[Path, Unknown | Unbound]" (reportUnknownArgumentType)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/Foundation/__init__.pyi
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/Foundation/__init__.pyi:3:47 - warning: Import "Optional" is not accessed (reportUnusedImport)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/Foundation/__init__.pyi:3:57 - warning: Import "Protocol" is not accessed (reportUnusedImport)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/Foundation/__init__.pyi:3:74 - warning: Import "Union" is not accessed (reportUnusedImport)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/objc/AppKit.pyi
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/objc/AppKit.pyi:87:5 - error: Type stub file is incomplete; "__getattr__" obscures type errors for module (reportIncompleteStub)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/objc/Foundation.pyi
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/objc/Foundation.pyi:10:5 - error: Type stub file is incomplete; "__getattr__" obscures type errors for module (reportIncompleteStub)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/objc/__init__.pyi
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/objc/__init__.pyi:3:45 - warning: Import "Protocol" is not accessed (reportUnusedImport)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/objc/__init__.pyi:3:70 - warning: Import "Union" is not accessed (reportUnusedImport)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/objc/objc.pyi
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/typings/objc/objc.pyi:5:5 - error: Type stub file is incomplete; "__getattr__" obscures type errors for module (reportIncompleteStub)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:65:28 - error: Unnecessary isinstance call; "ModuleType" is always an instance of "ModuleType" (reportUnnecessaryIsInstance)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:97:13 - error: Type of "initWithContentRect_styleMask_backing_defer_" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:97:37 - error: Cannot access attribute "initWithContentRect_styleMask_backing_defer_" for class "NSObject"
    Attribute "initWithContentRect_styleMask_backing_defer_" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:106:9 - error: Type of "_window" is partially unknown
    Type of "_window" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:106:9 - error: Type of "setTitle_" is partially unknown
    Type of "setTitle_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:107:9 - error: Type of "_window" is partially unknown
    Type of "_window" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:107:9 - error: Type of "setReleasedWhenClosed_" is partially unknown
    Type of "setReleasedWhenClosed_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:110:9 - error: Type of "content_view" is partially unknown
    Type of "content_view" is "Unknown | Any" (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:110:29 - error: Type of "_window" is partially unknown
    Type of "_window" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:110:29 - error: Type of "contentView" is partially unknown
    Type of "contentView" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:131:9 - error: Type of "addSubview_" is partially unknown
    Type of "addSubview_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:132:9 - error: Type of "addSubview_" is partially unknown
    Type of "addSubview_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/macos_app.py:133:9 - error: Type of "addSubview_" is partially unknown
    Type of "addSubview_" is "Unknown | Any" (reportUnknownMemberType)
/Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:34:34 - error: Type of "initWithFrame_" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:34:63 - error: Cannot access attribute "initWithFrame_" for class "NSObject"
    Attribute "initWithFrame_" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:95:32 - error: Type of "initWithFrame_" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:95:59 - error: Cannot access attribute "initWithFrame_" for class "NSObject"
    Attribute "initWithFrame_" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:98:33 - error: Type of "initWithFrame_" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:98:61 - error: Cannot access attribute "initWithFrame_" for class "NSObject"
    Attribute "initWithFrame_" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:105:9 - error: Type of "_scroll_view" is partially unknown
    Type of "_scroll_view" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:105:9 - error: Type of "setHasVerticalScroller_" is partially unknown
    Type of "setHasVerticalScroller_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:106:9 - error: Type of "_scroll_view" is partially unknown
    Type of "_scroll_view" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:106:9 - error: Type of "setHasHorizontalScroller_" is partially unknown
    Type of "setHasHorizontalScroller_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:107:9 - error: Type of "_scroll_view" is partially unknown
    Type of "_scroll_view" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:107:9 - error: Type of "setBorderType_" is partially unknown
    Type of "setBorderType_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:108:9 - error: Type of "_scroll_view" is partially unknown
    Type of "_scroll_view" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:108:9 - error: Type of "setAutoresizingMask_" is partially unknown
    Type of "setAutoresizingMask_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:111:9 - error: Type of "_scroll_view" is partially unknown
    Type of "_scroll_view" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:111:9 - error: Type of "setDocumentView_" is partially unknown
    Type of "setDocumentView_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:111:44 - error: Type of "_table_view" is partially unknown
    Type of "_table_view" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:121:9 - error: Type of "column" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:121:23 - error: Type of "initWithIdentifier_" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:121:52 - error: Cannot access attribute "initWithIdentifier_" for class "NSObject"
    Attribute "initWithIdentifier_" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:122:9 - error: Type of "setWidth_" is partially unknown
    Type of "setWidth_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:123:9 - error: Type of "headerCell" is partially unknown
    Type of "headerCell" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:123:9 - error: Type of "setStringValue_" is partially unknown
    Type of "setStringValue_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:180:29 - error: Type of "initWithFrame_" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:180:63 - error: Cannot access attribute "initWithFrame_" for class "NSObject"
    Attribute "initWithFrame_" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:186:9 - error: Type of "_control" is partially unknown
    Type of "_control" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:186:9 - error: Type of "setSegmentCount_" is partially unknown
    Type of "setSegmentCount_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:189:13 - error: Type of "_control" is partially unknown
    Type of "_control" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:189:13 - error: Type of "setLabel_forSegment_" is partially unknown
    Type of "setLabel_forSegment_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:190:13 - error: Type of "_control" is partially unknown
    Type of "_control" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:190:13 - error: Type of "setWidth_forSegment_" is partially unknown
    Type of "setWidth_forSegment_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:192:9 - error: Type of "_control" is partially unknown
    Type of "_control" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:192:9 - error: Type of "setTrackingMode_" is partially unknown
    Type of "setTrackingMode_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:193:9 - error: Type of "_control" is partially unknown
    Type of "_control" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:193:9 - error: Type of "setSegmentStyle_" is partially unknown
    Type of "setSegmentStyle_" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:194:9 - error: Type of "_control" is partially unknown
    Type of "_control" is "Unknown | Any" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/src/panoptikon/ui/objc_wrappers.py:194:9 - error: Type of "sizeToFit" is partially unknown
    Type of "sizeToFit" is "Unknown | Any" (reportUnknownMemberType)
/Users/james/Documents/GitHub/panoptikon/tests/conftest.py
  /Users/james/Documents/GitHub/panoptikon/tests/conftest.py:39:5 - error: Type of "set_value" is partially unknown
    Type of "set_value" is "set[Unknown]" (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/conftest.py:48:5 - warning: Function "_setup_test_env" is not accessed (reportUnusedFunction)
/Users/james/Documents/GitHub/panoptikon/tests/core/conftest.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/conftest.py:86:20 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/conftest.py:87:21 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/conftest.py:88:21 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:102:33 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:103:33 - error: "_active_scopes" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:104:33 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:113:33 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:114:52 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:124:26 - error: "_active_scopes" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:133:33 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:145:26 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:158:26 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:179:26 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:197:37 - error: "_path_to_filename" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:207:26 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:221:35 - error: "_save_bookmark" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:225:49 - error: "_path_to_filename" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:230:60 - error: "_read_bookmark_file" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:249:26 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:250:26 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:254:44 - error: "_path_to_filename" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:265:58 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:280:26 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:281:26 - error: "_active_scopes" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:282:26 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:290:58 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:299:26 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:331:30 - error: "_load_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:334:46 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:335:46 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:338:37 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:339:37 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:375:54 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:378:41 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:417:58 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:441:26 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:473:58 - error: "_active_scopes" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:474:41 - error: "_active_scopes" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:479:41 - error: "_active_scopes" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:490:60 - error: "_active_scopes" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:497:26 - error: "_bookmarks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:498:26 - error: "_active_scopes" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:505:33 - error: "_active_scopes" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:517:26 - error: "_active_scopes" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:528:37 - error: "_active_scopes" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:532:58 - error: "_active_scopes" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:578:43 - error: "_verify_bookmark" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:589:39 - error: "_verify_bookmark" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bookmarks.py:604:39 - error: "_verify_bookmark" is protected and used outside of the class in which it is declared (reportPrivateUsage)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_bootstrap.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bootstrap.py:54:9 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bootstrap.py:70:9 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bootstrap.py:79:60 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bootstrap.py:80:60 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bootstrap.py:88:9 - warning: Function "test_bootstrap_runs" is not accessed (reportUnusedFunction)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bootstrap.py:88:29 - error: Type of parameter "self" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_bootstrap.py:88:29 - error: Type annotation is missing for parameter "self" (reportMissingParameterType)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:31:33 - error: "_providers" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:32:33 - error: "_provider_roots" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:45:41 - error: "_check_provider_online" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:51:41 - error: "_check_provider_online" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:56:37 - error: "_check_provider_online" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:64:18 - error: "_providers" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:69:18 - error: "_provider_roots" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:88:18 - error: "_providers" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:93:18 - error: "_provider_roots" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:105:22 - error: "_providers" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:110:22 - error: "_provider_roots" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:135:18 - error: "_providers" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:136:18 - error: "_providers" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:139:35 - error: "_check_provider_online" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:145:18 - error: "_check_provider_online" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:153:29 - error: "_providers" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:154:25 - error: "_providers" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:157:18 - error: "_check_provider_online" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:240:22 - error: "_detector" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:272:22 - error: "_detector" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:295:22 - error: "_detector" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:298:22 - error: "_max_cache_size" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:307:33 - error: "_path_provider_cache" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:307:71 - error: "_max_cache_size" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:327:22 - error: "_detector" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:353:22 - error: "_detector" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:386:22 - error: "_detector" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:422:22 - error: "_detector" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_cloud_storage.py:457:22 - error: "_detector" is protected and used outside of the class in which it is declared (reportPrivateUsage)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_config.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_config.py:68:36 - error: "_schemas" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_config.py:124:42 - error: Argument of type "dict[str, str | int]" cannot be assigned to parameter "values" of type "dict[str, object]" in function "update_section"
    "dict[str, str | int]" is not assignable to "dict[str, object]"
      Type parameter "_VT@dict" is invariant, but "str | int" is not the same as "object"
      Consider switching from "dict" to "Mapping" which is covariant in the value type (reportArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_config.py:135:19 - error: "_config_dir" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_config.py:136:19 - error: "_config_file" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_config.py:146:29 - error: "_config_file" is protected and used outside of the class in which it is declared (reportPrivateUsage)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_config_hot_reload.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_config_hot_reload.py:129:23 - error: "_emit_config_change_events" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_config_hot_reload.py:144:50 - error: "_config_dir" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_config_hot_reload.py:161:34 - error: "_config_dir" is protected and used outside of the class in which it is declared (reportPrivateUsage)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_database_connection.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_connection.py:130:75 - error: Argument of type "list[tuple[int, str]]" cannot be assigned to parameter "parameters" of type "List[Tuple[object, ...] | Dict[str, object]]" in function "execute_many"
    "list[tuple[int, str]]" is not assignable to "List[Tuple[object, ...] | Dict[str, object]]"
      Type parameter "_T@list" is invariant, but "tuple[int, str]" is not the same as "Tuple[object, ...] | Dict[str, object]"
      Consider switching from "list" to "Sequence" which is covariant (reportArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_connection.py:169:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_connection.py:173:13 - error: Type of "thread" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_connection.py:174:13 - error: Type of "join" is unknown (reportUnknownMemberType)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:206:27 - error: "_check_version_compatibility" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:209:31 - error: "_check_version_compatibility" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:210:31 - error: "_check_version_compatibility" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:364:33 - error: "_find_migrations" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:374:24 - error: "_find_migrations" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:386:34 - error: "_migrate_1_0_0_to_1_1_0_with_backup" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:391:24 - error: Type of parameter "conn" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:391:24 - error: Type annotation is missing for parameter "conn" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:401:33 - error: "_find_migrations" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:412:34 - error: "_backup_database" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:418:59 - error: Type of parameter "caplog" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:418:59 - error: Type annotation is missing for parameter "caplog" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:422:10 - error: Type of "at_level" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:423:38 - error: "_backup_database" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:425:43 - error: Type of "m" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:425:48 - error: Type of "messages" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:435:20 - error: "_restore_database" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:450:34 - error: "_migrate_1_0_0_to_1_1_0_with_backup" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:483:24 - error: Type of parameter "conn" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_schema.py:483:24 - error: Type annotation is missing for parameter "conn" (reportMissingParameterType)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:42:24 - error: "_initialized" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:71:20 - error: "_initialized" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:72:20 - error: "_connection" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:73:20 - error: "_schema_manager" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:74:20 - error: "_config" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:75:20 - error: "_config" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:112:20 - error: "_initialized" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:115:20 - error: "_connection" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:116:31 - error: "_connection" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:120:28 - error: "_initialized" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:158:34 - error: "_connection" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:281:46 - error: "_schema_manager" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:284:38 - error: "_config" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:443:55 - error: Argument of type "list[tuple[int, str]]" cannot be assigned to parameter "parameters" of type "List[Tuple[Any, ...] | Dict[str, Any]]" in function "execute_many"
    "list[tuple[int, str]]" is not assignable to "List[Tuple[Any, ...] | Dict[str, Any]]"
      Type parameter "_T@list" is invariant, but "tuple[int, str]" is not the same as "Tuple[Any, ...] | Dict[str, Any]"
      Consider switching from "list" to "Sequence" which is covariant (reportArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:492:46 - error: Type of parameter "tmp_path" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:492:46 - error: Type annotation is missing for parameter "tmp_path" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:497:5 - error: Type of "db_path" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:498:28 - error: Argument type is unknown
    Argument corresponds to parameter "database" in function "connect" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:512:47 - error: Type of parameter "tmp_path" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:512:47 - error: Type annotation is missing for parameter "tmp_path" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:518:5 - error: Type of "db_path" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:519:28 - error: Argument type is unknown
    Argument corresponds to parameter "database" in function "connect" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:521:9 - error: "_cache_ttl" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:523:30 - error: "_statements" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:526:34 - error: "_statements" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:529:20 - error: "_statements" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_database_service.py:529:44 - error: "_cache_times" is protected and used outside of the class in which it is declared (reportPrivateUsage)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py:100:12 - error: Operator ">=" not supported for types "object" and "Literal[2]" (reportOperatorIssue)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py:122:45 - error: Operator "-" not supported for types "object" and "Literal[1]" (reportOperatorIssue)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py:166:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py:169:16 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py:174:12 - error: Operator ">=" not supported for types "object" and "object" (reportOperatorIssue)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py:220:12 - error: Operator ">" not supported for types "object" and "object" (reportOperatorIssue)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py:412:9 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py:414:9 - error: Type of "thread" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py:415:9 - error: Type of "join" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py:514:12 - error: Operator ">=" not supported for types "object" and "int" (reportOperatorIssue)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py:735:18 - error: "_checkout_connection" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool.py:745:14 - error: "_checkout_connection" is protected and used outside of the class in which it is declared (reportPrivateUsage)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:111:24 - error: "_initialized" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:181:49 - error: Cannot access attribute "return_value" for class "function"
    Attribute "return_value" is unknown (reportFunctionMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:237:78 - error: Argument of type "list[tuple[int, str]]" cannot be assigned to parameter "parameters" of type "List[Tuple[object, ...] | Dict[str, object]]" in function "execute_many"
    "list[tuple[int, str]]" is not assignable to "List[Tuple[object, ...] | Dict[str, object]]"
      Type parameter "_T@list" is invariant, but "tuple[int, str]" is not the same as "Tuple[object, ...] | Dict[str, object]"
      Consider switching from "list" to "Sequence" which is covariant (reportArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:256:27 - error: Cannot access attribute "return_value" for class "function"
    Attribute "return_value" is unknown (reportFunctionMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:264:27 - error: Cannot access attribute "assert_called_once_with" for class "function"
    Attribute "assert_called_once_with" is unknown (reportFunctionMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:278:25 - error: Cannot access attribute "return_value" for class "function"
    Attribute "return_value" is unknown (reportFunctionMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:286:25 - error: Cannot access attribute "assert_called_once_with" for class "function"
    Attribute "assert_called_once_with" is unknown (reportFunctionMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:300:30 - error: Cannot access attribute "return_value" for class "function"
    Attribute "return_value" is unknown (reportFunctionMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:308:30 - error: Cannot access attribute "assert_called_once_with" for class "function"
    Attribute "assert_called_once_with" is unknown (reportFunctionMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:325:25 - error: Cannot assign to attribute "return_value" for class "function"
    Attribute "return_value" is unknown (reportFunctionMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:331:25 - error: Cannot access attribute "assert_called_once" for class "function"
    Attribute "assert_called_once" is unknown (reportFunctionMemberAccess)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:345:29 - error: "_initialized" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:419:9 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:421:9 - error: Type of "thread" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:422:9 - error: Type of "join" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:516:12 - error: Operator ">=" not supported for types "object" and "Literal[1]" (reportOperatorIssue)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_db_pool_service.py:602:55 - error: Argument of type "list[tuple[int, str]]" cannot be assigned to parameter "parameters" of type "List[Tuple[object, ...] | Dict[str, object]]" in function "execute_many"
    "list[tuple[int, str]]" is not assignable to "List[Tuple[object, ...] | Dict[str, object]]"
      Type parameter "_T@list" is invariant, but "tuple[int, str]" is not the same as "Tuple[object, ...] | Dict[str, object]"
      Consider switching from "list" to "Sequence" which is covariant (reportArgumentType)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_errors.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_errors.py:141:26 - error: "_error_handlers" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_errors.py:142:26 - error: "_recovery_handlers" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_errors.py:143:26 - error: "_error_history" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_errors.py:144:26 - error: "_max_history_size" is protected and used outside of the class in which it is declared (reportPrivateUsage)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:276:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:288:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:317:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:320:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:323:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:326:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:404:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:407:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:429:20 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:430:16 - error: Type of "message" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:434:20 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:435:16 - error: Type of "message" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:473:16 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:474:16 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:475:16 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:476:16 - error: Type of "get" is partially unknown
    Type of "get" is "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:503:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:523:20 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:532:19 - error: "_event_loop" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:548:26 - error: "_event_loop" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:560:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:565:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:576:20 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:579:20 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:625:23 - error: "_deliver_event" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:637:23 - error: "_deliver_event" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:658:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:661:13 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:674:20 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:677:20 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:679:16 - error: Type of "special_data" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:686:20 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_events.py:689:20 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:116:20 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:117:21 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:118:21 - error: "_bookmark_storage_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:543:20 - error: Type of "match_rule_set" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:543:33 - error: Cannot access attribute "match_rule_set" for class "PathManager"
    Attribute "match_rule_set" is unknown (reportAttributeAccessIssue)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:554:9 - error: Type of parameter "mocker" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:554:9 - error: Type annotation is missing for parameter "mocker" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:561:9 - error: Type of "provider" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:561:20 - error: Type of "Mock" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:562:9 - error: Type of "patch" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:562:9 - error: Type of "object" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:565:9 - error: Type of "patch" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:565:9 - error: Type of "object" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:566:9 - error: Type of "patch" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:566:9 - error: Type of "object" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:567:9 - error: Type of "patch" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:567:9 - error: Type of "object" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:589:9 - error: Type of parameter "mocker" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:589:9 - error: Type annotation is missing for parameter "mocker" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:594:9 - error: Type of "patch" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:594:9 - error: Type of "object" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:595:9 - error: Type of "patch" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:595:9 - error: Type of "object" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:596:9 - error: Type of "patch" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem.py:596:9 - error: Type of "object" is unknown (reportUnknownMemberType)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:97:37 - error: "_standard_write" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:106:33 - error: "_standard_delete" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:114:33 - error: "_standard_rename" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:124:39 - error: "_standard_read" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:134:39 - error: "_standard_write" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:137:39 - error: "_standard_write" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:146:39 - error: "_standard_delete" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:155:39 - error: "_standard_rename" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:164:39 - error: "_standard_move" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:172:39 - error: "_standard_create" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:181:39 - error: "_standard_metadata" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:187:34 - error: "_get_operation_handler" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:195:24 - error: "_provider_operations" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:196:34 - error: "_get_operation_handler" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:200:66 - error: Type of parameter "caplog" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:200:66 - error: Type annotation is missing for parameter "caplog" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:203:14 - error: Type of "at_level" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:204:37 - error: "_cloud_operation_not_implemented" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:206:57 - error: Type of "m" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:206:62 - error: Type of "messages" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:217:33 - error: "_handle_access_denied" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:222:66 - error: Type of parameter "mocker" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:222:66 - error: Type annotation is missing for parameter "mocker" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:230:9 - error: Type of "publish_spy" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:230:23 - error: Type of "spy" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:231:33 - error: "_handle_access_denied" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:234:9 - error: Type of "assert_called_once" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:237:66 - error: Type of parameter "mocker" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:237:66 - error: Type annotation is missing for parameter "mocker" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:246:9 - error: Type of "patch" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:246:9 - error: Type of "object" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:247:75 - error: Type of parameter "_" is unknown (reportUnknownLambdaType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:254:66 - error: Type of parameter "mocker" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:254:66 - error: Type annotation is missing for parameter "mocker" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:263:9 - error: Type of "patch" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:263:9 - error: Type of "object" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:264:75 - error: Type of parameter "_" is unknown (reportUnknownLambdaType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:308:28 - error: "_bookmark_service" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:312:37 - error: "_handle_bookmark_access" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:324:28 - error: "_bookmark_service" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_access.py:328:37 - error: "_handle_bookmark_access" is protected and used outside of the class in which it is declared (reportPrivateUsage)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:65:28 - error: "_watching" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:66:24 - error: "_interval" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:67:24 - error: "_watches" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:68:24 - error: "_recursive_watches" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:73:24 - error: "_watching" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:74:24 - error: "_thread" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:76:28 - error: "_watching" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:82:32 - error: "_watches" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:86:36 - error: "_watches" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:104:17 - error: Type of "append" is partially unknown
    Type of "append" is "(object: Unknown, /) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:105:20 - error: Argument type is partially unknown
    Argument corresponds to parameter "obj" in function "len"
    Argument type is "list[Unknown]" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:108:40 - error: Type of parameter "caplog" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:108:40 - error: Type annotation is missing for parameter "caplog" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:112:14 - error: Type of "at_level" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:114:44 - error: "_watches" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:115:68 - error: Type of "m" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:115:73 - error: Type of "messages" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:118:40 - error: Type of parameter "caplog" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:118:40 - error: Type annotation is missing for parameter "caplog" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:122:14 - error: Type of "at_level" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:124:54 - error: Type of "m" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:124:59 - error: Type of "messages" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:127:55 - error: Type of parameter "caplog" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:127:55 - error: Type annotation is missing for parameter "caplog" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:132:14 - error: Type of "at_level" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:134:58 - error: Type of "m" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:134:63 - error: Type of "messages" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:135:29 - error: "_watches" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:138:55 - error: Type of parameter "caplog" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:138:55 - error: Type annotation is missing for parameter "caplog" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:144:14 - error: Type of "at_level" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:146:54 - error: Type of "m" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:146:59 - error: Type of "messages" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:149:55 - error: Type of parameter "caplog" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:149:55 - error: Type annotation is missing for parameter "caplog" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:156:18 - error: Type of "at_level" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:157:25 - error: "_refresh_watch_state" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:158:60 - error: Type of "m" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:158:65 - error: Type of "messages" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:161:55 - error: Type of parameter "caplog" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:161:55 - error: Type annotation is missing for parameter "caplog" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:167:18 - error: Type of "at_level" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:168:34 - error: "_scan_directory" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:170:56 - error: Type of "m" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:170:61 - error: Type of "messages" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:180:17 - error: "_watches" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:181:17 - error: "_handle_deleted_path" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:190:24 - error: "_watches" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:195:24 - error: "_thread" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:197:24 - error: "_thread" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:198:28 - error: "_watching" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:206:36 - error: "_recursive_watches" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:208:32 - error: "_recursive_watches" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:226:25 - error: "_watcher_type" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:228:25 - error: "_create_watcher" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:229:43 - error: "_watcher" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:240:21 - error: "_stop_event" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:242:21 - error: "_watch_thread" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:251:17 - error: "_event_callback" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:252:17 - error: "_process_new_and_modified_files" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:267:17 - error: "_event_callback" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:268:17 - error: "_process_deleted_files" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:281:17 - error: "_event_callback" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:284:17 - error: "_emit_file_event" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:296:28 - error: "_watching" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:306:31 - error: "_watcher" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:309:24 - error: "_watcher" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:312:35 - error: "_watcher" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:321:39 - error: "_watcher" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:333:24 - error: "_watcher" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:346:46 - error: "_watched_paths" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:355:17 - error: "_watcher_type" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:361:21 - error: "_create_watcher" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:362:35 - error: "_watcher" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:364:59 - error: Type of parameter "mocker" is unknown (reportUnknownParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:364:59 - error: Type annotation is missing for parameter "mocker" (reportMissingParameterType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:373:9 - error: Type of "event_callback" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:373:26 - error: Type of "Mock" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:374:35 - error: Argument type is unknown
    Argument corresponds to parameter "event_callback" in function "__init__" (reportUnknownArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:379:9 - error: Type of "_streams" is partially unknown
    Type of "_streams" is "dict[Path, Unknown | Unbound]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:379:17 - error: "_streams" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:379:34 - error: Type of "Mock" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:383:28 - error: Type of "_streams" is partially unknown
    Type of "_streams" is "dict[Path, Unknown | Unbound]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:383:36 - error: "_streams" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:403:28 - error: "_watching" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:404:24 - error: "_latency" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:405:16 - error: Type of "_streams" is partially unknown
    Type of "_streams" is "dict[Path, Unknown | Unbound]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:405:24 - error: "_streams" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:410:24 - error: "_watching" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:411:16 - error: Type of "_observer" is partially unknown
    Type of "_observer" is "Unknown | None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:411:24 - error: "_observer" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:413:28 - error: "_watching" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:414:16 - error: Type of "_observer" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:414:24 - error: "_observer" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:420:24 - error: Type of "_streams" is partially unknown
    Type of "_streams" is "dict[Path, Unknown | Unbound]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:420:32 - error: "_streams" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:424:28 - error: Type of "_streams" is partially unknown
    Type of "_streams" is "dict[Path, Unknown | Unbound]" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:424:36 - error: "_streams" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:434:30 - error: "_watcher" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:445:48 - error: "_watched_paths" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_filesystem_watcher.py:462:52 - error: "_watched_paths" is protected and used outside of the class in which it is declared (reportPrivateUsage)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_integration.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_integration.py:35:21 - error: Base class type is unknown, obscuring type of derived class (reportUntypedBaseClass)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_integration.py:46:13 - error: Type of "__init__" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_integration.py:55:13 - error: Type of "result" is unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_integration.py:55:38 - error: Type of "to_dict" is unknown (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_integration.py:59:20 - error: Return type, "Unknown | dict[str, Any]", is partially unknown (reportUnknownVariableType)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_integration.py:95:15 - error: "_instances" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_integration.py:96:15 - error: "_instances" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_integration.py:112:15 - error: "_instances" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_integration.py:113:15 - error: "_instances" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_integration.py:114:15 - error: "_instances" is protected and used outside of the class in which it is declared (reportPrivateUsage)
/Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py:40:22 - error: "_startup_hooks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py:41:22 - error: "_shutdown_hooks" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py:42:22 - error: "_exit_code" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py:110:22 - error: "_state" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py:113:15 - error: "_change_state" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py:114:22 - error: "_state" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py:118:15 - error: "_change_state" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py:119:22 - error: "_state" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py:123:15 - error: "_change_state" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py:124:22 - error: "_state" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py:128:15 - error: "_change_state" is protected and used outside of the class in which it is declared (reportPrivateUsage)
  /Users/james/Documents/GitHub/panoptikon/tests/core/test_lifecycle.py:129:22 - error: "_state" is protected and used outside of the class in which it is declared (reportPrivateUsage)
/Users/james/Documents/GitHub/panoptikon/tests/events_patched.py
  /Users/james/Documents/GitHub/panoptikon/tests/events_patched.py:286:21 - error: Argument of type "AsyncEventHandler[T@subscribe] | AsyncEventHandler[Unknown] | ((T@subscribe) -> Coroutine[Any, Any, Any]) | EventHandler[T@subscribe] | ((T@subscribe) -> None) | ((T@subscribe) -> Future[None])" cannot be assigned to parameter "handler" of type "EventHandler[Any] | AsyncEventHandler[Any] | ((Any) -> None) | ((Any) -> Future[None])" in function "__init__"
    Type "AsyncEventHandler[T@subscribe] | AsyncEventHandler[Unknown] | ((T@subscribe) -> Coroutine[Any, Any, Any]) | EventHandler[T@subscribe] | ((T@subscribe) -> None) | ((T@subscribe) -> Future[None])" is not assignable to type "EventHandler[Any] | AsyncEventHandler[Any] | ((Any) -> None) | ((Any) -> Future[None])"
      Type "(T@subscribe) -> Coroutine[Any, Any, Any]" is not assignable to type "EventHandler[Any] | AsyncEventHandler[Any] | ((Any) -> None) | ((Any) -> Future[None])"
        "function" is not assignable to "EventHandler[Any]"
        "function" is not assignable to "AsyncEventHandler[Any]"
        Type "(T@subscribe) -> Coroutine[Any, Any, Any]" is not assignable to type "(Any) -> None"
          Function return type "Coroutine[Any, Any, Any]" is incompatible with type "None"
            "Coroutine[Any, Any, Any]" is not assignable to "None"
        Type "(T@subscribe) -> Coroutine[Any, Any, Any]" is not assignable to type "(Any) -> Future[None]"
    ... (reportArgumentType)
  /Users/james/Documents/GitHub/panoptikon/tests/events_patched.py:417:13 - error: Type of "handle" is partially unknown
    Type of "handle" is "(event: Unknown) -> None" (reportUnknownMemberType)
  /Users/james/Documents/GitHub/panoptikon/tests/events_patched.py:434:42 - error: Type of "handle" is partially unknown
    Type of "handle" is "(event: Unknown) -> CoroutineType[Any, Any, None]" (reportUnknownMemberType)
/Users/james/Documents/GitHub/panoptikon/tests/test_main.py
  /Users/james/Documents/GitHub/panoptikon/tests/test_main.py:111:24 - error: Return type is unknown (reportUnknownVariableType)
687 errors, 9 warnings, 0 informations 
