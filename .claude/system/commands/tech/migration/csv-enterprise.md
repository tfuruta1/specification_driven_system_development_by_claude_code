# /csv-enterprise - CSV

## 
CSV100GB

## 
```bash
/csv-enterprise [action] [options]

# 
/csv-enterprise import --file=large.csv --streaming --parallel=8
/csv-enterprise validate --schema=rules.json --output-errors=errors.csv
/csv-enterprise transform --encoding=auto --delimiter=auto
/csv-enterprise export --format=parquet --compression=snappy
/csv-enterprise profile --deep-analysis --sample-size=10000
```

## CSV ANALYSIS

### 1. ANALYSIS
```python
# streaming/csv_streamer.py
import csv
import io
import chardet
import pandas as pd
from typing import Iterator, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
import aiofiles
from concurrent.futures import ProcessPoolExecutor
import numpy as np

@dataclass
class StreamConfig:
    chunk_size: int = 10000
    encoding: str = 'auto'
    delimiter: str = 'auto'
    compression: Optional[str] = None
    parallel_workers: int = 8
    memory_limit_mb: int = 500

class EnterpriseCSVStreamer:
    def __init__(self, config: StreamConfig):
        self.config = config
        self.encoding_cache = {}
        self.delimiter_cache = {}
        self.executor = ProcessPoolExecutor(max_workers=config.parallel_workers)
        
    async def stream_process(self, 
                            filepath: str, 
                            processor_func: callable) -> Iterator[pd.DataFrame]:
        """CSV"""
        
        # 
        encoding = await self._detect_encoding(filepath)
        
        # 
        delimiter = await self._detect_delimiter(filepath, encoding)
        
        # 
        compression = self._detect_compression(filepath)
        
        # 
        async with aiofiles.open(filepath, mode='r', encoding=encoding) as file:
            # 
            header_line = await file.readline()
            headers = self._parse_header(header_line, delimiter)
            
            # 
            chunk_buffer = []
            line_count = 0
            
            async for line in file:
                chunk_buffer.append(line)
                line_count += 1
                
                if line_count >= self.config.chunk_size:
                    # CONFIG
                    df_chunk = await self._process_chunk(
                        chunk_buffer, headers, delimiter, processor_func
                    )
                    yield df_chunk
                    
                    # 
                    chunk_buffer = []
                    line_count = 0
                    await self._check_memory_usage()
            
            # ANALYSIS
            if chunk_buffer:
                df_chunk = await self._process_chunk(
                    chunk_buffer, headers, delimiter, processor_func
                )
                yield df_chunk
    
    async def _detect_encoding(self, filepath: str) -> str:
        """"""
        if filepath in self.encoding_cache:
            return self.encoding_cache[filepath]
        
        # 
        encodings_to_try = []
        
        # chardet 
        async with aiofiles.open(filepath, 'rb') as file:
            sample = await file.read(100000)  # 100KB
            detected = chardet.detect(sample)
            if detected['confidence'] > 0.7:
                encodings_to_try.append(detected['encoding'])
        
        # 
        encodings_to_try.extend(['utf-8', 'shift-jis', 'cp932', 'euc-jp', 'iso-2022-jp'])
        
        # 
        for encoding in encodings_to_try:
            try:
                async with aiofiles.open(filepath, 'r', encoding=encoding) as file:
                    await file.read(10000)  # 
                self.encoding_cache[filepath] = encoding
                return encoding
            except UnicodeDecodeError:
                continue
        
        # ERROR
        return 'utf-8'
    
    async def _detect_delimiter(self, filepath: str, encoding: str) -> str:
        """"""
        cache_key = f"{filepath}:{encoding}"
        if cache_key in self.delimiter_cache:
            return self.delimiter_cache[cache_key]
        
        async with aiofiles.open(filepath, 'r', encoding=encoding) as file:
            sample = await file.read(10000)
        
        # 
        sniffer = csv.Sniffer()
        try:
            delimiter = sniffer.sniff(sample).delimiter
        except:
            # 
            delimiters = [',', '\t', ';', '|', ' ']
            delimiter_counts = {d: sample.count(d) for d in delimiters}
            delimiter = max(delimiter_counts, key=delimiter_counts.get)
        
        self.delimiter_cache[cache_key] = delimiter
        return delimiter
    
    async def _process_chunk(self, 
                           lines: list, 
                           headers: list, 
                           delimiter: str,
                           processor_func: callable) -> pd.DataFrame:
        """"""
        
        # CSV 
        csv_data = []
        for line in lines:
            try:
                row = list(csv.reader([line], delimiter=delimiter))[0]
                csv_data.append(row)
            except:
                # ERROR
                self._log_error_row(line)
                continue
        
        # DataFrame ERROR
        df = pd.DataFrame(csv_data, columns=headers)
        
        # 
        if processor_func:
            df = await asyncio.get_event_loop().run_in_executor(
                self.executor, processor_func, df
            )
        
        return df
    
    async def _check_memory_usage(self):
        """ANALYSIS"""
        import psutil
        import gc
        
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > self.config.memory_limit_mb:
            gc.collect()
            
            # CONFIG
            if memory_mb > self.config.memory_limit_mb * 1.2:
                await asyncio.sleep(1)

# CONFIGCSVCONFIG
class ParallelCSVMerger:
    """TASKCSVTASK"""
    
    def __init__(self, num_workers: int = 8):
        self.num_workers = num_workers
        
    async def merge_files(self, 
                         file_patterns: list,
                         output_file: str,
                         merge_key: Optional[str] = None):
        """"""
        
        # 
        import glob
        all_files = []
        for pattern in file_patterns:
            all_files.extend(glob.glob(pattern))
        
        if merge_key:
            # REPORT
            result = await self._merge_with_key(all_files, merge_key)
        else:
            # REPORT
            result = await self._concat_files(all_files)
        
        # REPORT
        await self._write_output(result, output_file)
        
    async def _merge_with_key(self, files: list, key: str) -> pd.DataFrame:
        """TASK"""
        
        tasks = []
        for file in files:
            task = asyncio.create_task(self._read_file_async(file))
            tasks.append(task)
        
        dataframes = await asyncio.gather(*tasks)
        
        # TASK
        result = dataframes[0]
        for df in dataframes[1:]:
            result = pd.merge(result, df, on=key, how='outer')
        
        return result
    
    async def _concat_files(self, files: list) -> pd.DataFrame:
        """TASK"""
        
        # TASK
        chunk_size = len(files) // self.num_workers + 1
        chunks = [files[i:i+chunk_size] for i in range(0, len(files), chunk_size)]
        
        tasks = []
        for chunk in chunks:
            task = asyncio.create_task(self._read_chunk(chunk))
            tasks.append(task)
        
        chunk_results = await asyncio.gather(*tasks)
        
        # TASK
        return pd.concat(chunk_results, ignore_index=True)
```

### 2. REPORT
```python
# validation/csv_validator.py
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import jsonschema
import pandas as pd

class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationRule:
    field: str
    rule_type: str
    parameters: Dict[str, Any]
    severity: ValidationSeverity
    message: str

class EnterpriseCSVValidator:
    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.custom_validators = {}
        self.validation_stats = {
            'total_rows': 0,
            'valid_rows': 0,
            'error_rows': 0,
            'warning_rows': 0
        }
        
    def add_rule(self, rule: ValidationRule):
        """WARNING"""
        self.rules.append(rule)
        
    def register_custom_validator(self, name: str, func: callable):
        """"""
        self.custom_validators[name] = func
        
    async def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """DataFrameERROR"""
        
        errors = []
        warnings = []
        
        # ERROR
        for idx, row in df.iterrows():
            self.validation_stats['total_rows'] += 1
            row_errors = []
            row_warnings = []
            
            for rule in self.rules:
                result = await self._apply_rule(row, rule)
                
                if not result['valid']:
                    if rule.severity == ValidationSeverity.ERROR:
                        row_errors.append({
                            'row': idx,
                            'field': rule.field,
                            'value': row.get(rule.field),
                            'message': result['message']
                        })
                    elif rule.severity == ValidationSeverity.WARNING:
                        row_warnings.append({
                            'row': idx,
                            'field': rule.field,
                            'value': row.get(rule.field),
                            'message': result['message']
                        })
            
            if row_errors:
                self.validation_stats['error_rows'] += 1
                errors.extend(row_errors)
            elif not row_warnings:
                self.validation_stats['valid_rows'] += 1
            
            if row_warnings:
                self.validation_stats['warning_rows'] += 1
                warnings.extend(row_warnings)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'stats': self.validation_stats
        }
    
    async def _apply_rule(self, row: pd.Series, rule: ValidationRule) -> Dict[str, Any]:
        """"""
        
        value = row.get(rule.field)
        
        # 
        validators = {
            'required': self._validate_required,
            'type': self._validate_type,
            'format': self._validate_format,
            'range': self._validate_range,
            'length': self._validate_length,
            'pattern': self._validate_pattern,
            'unique': self._validate_unique,
            'reference': self._validate_reference,
            'custom': self._validate_custom
        }
        
        validator = validators.get(rule.rule_type)
        if validator:
            return await validator(value, rule.parameters)
        
        return {'valid': True}
    
    async def _validate_required(self, value: Any, params: Dict) -> Dict:
        """"""
        if pd.isna(value) or value == '':
            return {
                'valid': False,
                'message': ''
            }
        return {'valid': True}
    
    async def _validate_type(self, value: Any, params: Dict) -> Dict:
        """ANALYSIS"""
        expected_type = params.get('type')
        
        type_checkers = {
            'integer': lambda x: str(x).isdigit(),
            'float': lambda x: self._is_float(x),
            'date': lambda x: self._is_date(x, params.get('format')),
            'email': lambda x: self._is_email(x),
            'phone': lambda x: self._is_phone(x),
            'postal_code': lambda x: self._is_postal_code(x)
        }
        
        checker = type_checkers.get(expected_type)
        if checker and not checker(value):
            return {
                'valid': False,
                'message': f'ANALYSIS: {expected_type}'
            }
        
        return {'valid': True}
    
    def _is_float(self, value: Any) -> bool:
        """"""
        try:
            float(str(value).replace(',', ''))
            return True
        except:
            return False
    
    def _is_date(self, value: Any, format: Optional[str] = None) -> bool:
        """"""
        if pd.isna(value):
            return False
            
        formats = [format] if format else [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d/%m/%Y',
            '%Y%m%d',
            '%Y-%m-%d %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                pd.to_datetime(value, format=fmt)
                return True
            except:
                continue
        
        return False
    
    def _is_email(self, value: Any) -> bool:
        """"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(value)))
    
    def _is_phone(self, value: Any) -> bool:
        """"""
        pattern = r'^(0\d{1,4}-?\d{1,4}-?\d{4}|0\d{9,10})$'
        cleaned = re.sub(r'[^\d]', '', str(value))
        return bool(re.match(pattern, cleaned))
    
    def _is_postal_code(self, value: Any) -> bool:
        """"""
        pattern = r'^\d{3}-?\d{4}$'
        return bool(re.match(pattern, str(value)))

# REPORT
class CSVProfiler:
    """CSVREPORT"""
    
    def __init__(self):
        self.profile_results = {}
        
    async def profile(self, df: pd.DataFrame, deep: bool = False) -> Dict[str, Any]:
        """"""
        
        profile = {
            'basic_stats': self._get_basic_stats(df),
            'data_types': self._analyze_data_types(df),
            'missing_values': self._analyze_missing_values(df),
            'uniqueness': self._analyze_uniqueness(df),
            'patterns': self._detect_patterns(df)
        }
        
        if deep:
            profile.update({
                'correlations': self._calculate_correlations(df),
                'outliers': self._detect_outliers(df),
                'distributions': self._analyze_distributions(df)
            })
        
        return profile
    
    def _get_basic_stats(self, df: pd.DataFrame) -> Dict:
        """"""
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024 / 1024,  # MB
            'duplicate_rows': df.duplicated().sum()
        }
    
    def _analyze_data_types(self, df: pd.DataFrame) -> Dict:
        """REPORT"""
        type_summary = {}
        
        for col in df.columns:
            # REPORT
            inferred_type = self._infer_column_type(df[col])
            
            type_summary[col] = {
                'pandas_type': str(df[col].dtype),
                'inferred_type': inferred_type,
                'sample_values': df[col].dropna().head(5).tolist()
            }
        
        return type_summary
    
    def _infer_column_type(self, series: pd.Series) -> str:
        """REPORT"""
        
        # 
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return 'empty'
        
        # ANALYSIS
        checkers = [
            ('integer', lambda s: s.apply(lambda x: str(x).isdigit()).all()),
            ('float', lambda s: s.apply(lambda x: self._is_numeric(x)).all()),
            ('date', lambda s: pd.to_datetime(s, errors='coerce').notna().all()),
            ('boolean', lambda s: s.isin([True, False, 'true', 'false', '0', '1']).all()),
            ('email', lambda s: s.apply(lambda x: '@' in str(x)).all()),
            ('url', lambda s: s.apply(lambda x: str(x).startswith(('http://', 'https://'))).all()),
            ('json', lambda s: s.apply(lambda x: self._is_json(x)).all())
        ]
        
        for type_name, checker in checkers:
            try:
                if checker(non_null):
                    return type_name
            except:
                continue
        
        return 'string'
    
    def _is_numeric(self, value: Any) -> bool:
        """"""
        try:
            float(str(value).replace(',', ''))
            return True
        except:
            return False
    
    def _is_json(self, value: Any) -> bool:
        """JSON"""
        import json
        try:
            json.loads(str(value))
            return True
        except:
            return False
```

### 3. 
```python
# transform/csv_transformer.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import pyarrow as pa
import pyarrow.parquet as pq

class EnterpriseCSVTransformer:
    """CSV"""
    
    def __init__(self):
        self.transformation_pipeline = []
        self.custom_transformers = {}
        
    def add_transformation(self, 
                         field: str, 
                         transform_type: str, 
                         params: Dict[str, Any]):
        """"""
        self.transformation_pipeline.append({
            'field': field,
            'type': transform_type,
            'params': params
        })
        
    async def transform_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrameREPORT"""
        
        result_df = df.copy()
        
        for transform in self.transformation_pipeline:
            field = transform['field']
            transform_type = transform['type']
            params = transform['params']
            
            if field not in result_df.columns:
                continue
            
            # REPORT
            transformers = {
                'normalize': self._normalize_column,
                'standardize': self._standardize_column,
                'encode': self._encode_column,
                'split': self._split_column,
                'merge': self._merge_columns,
                'pivot': self._pivot_data,
                'aggregate': self._aggregate_data,
                'clean': self._clean_data,
                'format': self._format_data
            }
            
            transformer = transformers.get(transform_type)
            if transformer:
                result_df = await transformer(result_df, field, params)
        
        return result_df
    
    async def _normalize_column(self, df: pd.DataFrame, field: str, params: Dict) -> pd.DataFrame:
        """"""
        method = params.get('method', 'min-max')
        
        if method == 'min-max':
            min_val = df[field].min()
            max_val = df[field].max()
            df[field] = (df[field] - min_val) / (max_val - min_val)
        elif method == 'z-score':
            mean = df[field].mean()
            std = df[field].std()
            df[field] = (df[field] - mean) / std
        
        return df
    
    async def _encode_column(self, df: pd.DataFrame, field: str, params: Dict) -> pd.DataFrame:
        """"""
        encoding_type = params.get('type', 'label')
        
        if encoding_type == 'label':
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            df[field] = le.fit_transform(df[field])
        elif encoding_type == 'one-hot':
            df = pd.get_dummies(df, columns=[field], prefix=field)
        elif encoding_type == 'ordinal':
            mapping = params.get('mapping', {})
            df[field] = df[field].map(mapping)
        
        return df
    
    async def _clean_data(self, df: pd.DataFrame, field: str, params: Dict) -> pd.DataFrame:
        """"""
        
        # 
        if params.get('trim', True):
            df[field] = df[field].astype(str).str.strip()
        
        # 
        if params.get('normalize_width', False):
            import unicodedata
            df[field] = df[field].apply(
                lambda x: unicodedata.normalize('NFKC', str(x))
            )
        
        # 
        if params.get('remove_special', False):
            df[field] = df[field].str.replace(r'[^\w\s]', '', regex=True)
        
        # NULL
        null_strategy = params.get('null_strategy', 'keep')
        if null_strategy == 'remove':
            df = df.dropna(subset=[field])
        elif null_strategy == 'fill':
            fill_value = params.get('fill_value', '')
            df[field] = df[field].fillna(fill_value)
        elif null_strategy == 'interpolate':
            df[field] = df[field].interpolate()
        
        return df

# 
class FastCSVExporter:
    """CSV/Parquet"""
    
    def __init__(self):
        self.compression_options = {
            'gzip': {'method': 'gzip', 'compresslevel': 9},
            'bz2': {'method': 'bz2', 'compresslevel': 9},
            'xz': {'method': 'xz'},
            'snappy': {'compression': 'snappy'}
        }
        
    async def export_to_parquet(self, 
                               df: pd.DataFrame, 
                               output_path: str,
                               compression: str = 'snappy',
                               partition_cols: Optional[List[str]] = None):
        """Parquet"""
        
        # PyArrow
        table = pa.Table.from_pandas(df)
        
        # 
        if partition_cols:
            pq.write_to_dataset(
                table,
                root_path=output_path,
                partition_cols=partition_cols,
                compression=compression
            )
        else:
            pq.write_table(
                table,
                output_path,
                compression=compression
            )
    
    async def export_to_csv_chunked(self,
                                   df: pd.DataFrame,
                                   output_path: str,
                                   chunk_size: int = 100000):
        """CSV"""
        
        total_rows = len(df)
        num_chunks = (total_rows // chunk_size) + 1
        
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, total_rows)
            
            chunk_df = df.iloc[start_idx:end_idx]
            
            # 
            if num_chunks > 1:
                chunk_path = output_path.replace('.csv', f'_part{i+1:03d}.csv')
            else:
                chunk_path = output_path
            
            # 
            chunk_df.to_csv(
                chunk_path,
                index=False,
                encoding='utf-8-sig',  # Excel
                chunksize=10000
            )
```

## 
```markdown
# CSV 

## 
[OK] : 50GB
[OK] : 530
[OK] : 151.5MB/
[OK] :  480MB
[OK] : 1270.001%

## 
- : 99.999%
- : 2.3%
- : 0.05%
- : 0.02%

## 
- : 15
- : 8
- : 
- : Parquet 85%

## 
- : 
- : 8
- : 10,000
- I/O: 
```

## 
- ****: 
- ****: CSVETL

---
*CSV*