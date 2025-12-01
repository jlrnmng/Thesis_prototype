#!/usr/bin/env python3
"""
ChromaDB Schema Analysis and Visualization Tool

This script analyzes the ChromaDB database schema and creates visualizations of:
1. Database structure and collections
2. Document distribution across collections
3. Metadata field analysis
4. Content analysis and statistics

Saves visualizations as PNG images in the scripts/visualizations/ directory.
"""
import os
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
from collections import Counter
import re

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def setup_visualization_dir():
    """Create visualization output directory"""
    viz_dir = os.path.join(os.path.dirname(__file__), 'visualizations')
    os.makedirs(viz_dir, exist_ok=True)
    return viz_dir

def analyze_chroma_collections():
    """Analyze ChromaDB collections using the app's configuration"""
    import chromadb
    from chromadb.config import Settings
    
    try:
        # Set environment variables to disable telemetry
        os.environ['CHROMA_DISABLE_TELEMETRY'] = '1'
        os.environ['ANONYMIZED_TELEMETRY'] = 'False'
        
        # Get ChromaDB path
        chroma_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'chroma_storage'
        ))
        print(f"Analyzing ChromaDB at: {chroma_path}")
        
        # Initialize ChromaDB client with correct API
        try:
            # Try newer API first
            client = chromadb.PersistentClient(path=chroma_path)
        except AttributeError:
            # Fall back to older API
            client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=chroma_path
            ))
        
        # Get all collections
        collections = client.list_collections()
        print(f"Found {len(collections)} collections")
        
        schema_info = {
            'collections': [],
            'total_documents': 0,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        collection_data = {}
        
        for collection in collections:
            coll_name = collection.name
            print(f"\nAnalyzing collection: {coll_name}")
            
            # Get collection data
            try:
                coll = client.get_collection(coll_name)
                # Get data with default includes (should get everything)
                data = coll.get()
                
                doc_count = len(data.get('ids', []))
                
                collection_info = {
                    'name': coll_name,
                    'document_count': doc_count,
                    'sample_ids': data.get('ids', [])[:5],
                    'metadata_fields': [],
                    'id_patterns': [],
                    'document_lengths': []
                }
                
                # Analyze metadata structure
                if data.get('metadatas'):
                    all_fields = set()
                    for metadata in data['metadatas']:
                        if metadata:
                            all_fields.update(metadata.keys())
                    collection_info['metadata_fields'] = list(all_fields)
                
                # Analyze ID patterns
                if data.get('ids'):
                    id_patterns = {}
                    for doc_id in data['ids']:
                        pattern = doc_id.split('_')[0] if '_' in doc_id else 'other'
                        id_patterns[pattern] = id_patterns.get(pattern, 0) + 1
                    collection_info['id_patterns'] = id_patterns
                
                # Analyze document lengths
                if data.get('documents'):
                    collection_info['document_lengths'] = [
                        len(doc) if doc else 0 for doc in data['documents']
                    ]
                
                schema_info['collections'].append(collection_info)
                schema_info['total_documents'] += doc_count
                
                # Store full data for visualization
                collection_data[coll_name] = {
                    'ids': data.get('ids', []),
                    'documents': data.get('documents', []),
                    'metadatas': data.get('metadatas', []),
                    'count': doc_count
                }
                
                print(f"  - Documents: {doc_count}")
                print(f"  - Metadata fields: {collection_info['metadata_fields']}")
                print(f"  - ID patterns: {collection_info['id_patterns']}")
                
            except Exception as e:
                print(f"Error analyzing collection {coll_name}: {e}")
                continue
        
        return schema_info, collection_data
        
    except Exception as e:
        print(f"Error connecting to ChromaDB: {e}")
        return None, None

def create_collection_overview_plot(schema_info, viz_dir):
    """Create overview plot of collections and document counts"""
    if not schema_info or not schema_info['collections']:
        print("No collection data to visualize")
        return
    
    # Prepare data
    collection_names = [c['name'] for c in schema_info['collections']]
    doc_counts = [c['document_count'] for c in schema_info['collections']]
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('ChromaDB Schema Analysis Overview', fontsize=16, fontweight='bold')
    
    # 1. Document count by collection (bar chart)
    colors = sns.color_palette("husl", len(collection_names))
    bars = ax1.bar(collection_names, doc_counts, color=colors)
    ax1.set_title('Document Count by Collection')
    ax1.set_xlabel('Collection')
    ax1.set_ylabel('Document Count')
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    # 2. Collection distribution (pie chart)
    if sum(doc_counts) > 0:
        ax2.pie(doc_counts, labels=collection_names, autopct='%1.1f%%', 
                colors=colors, startangle=90)
        ax2.set_title('Document Distribution Across Collections')
    else:
        ax2.text(0.5, 0.5, 'No documents found', ha='center', va='center')
        ax2.set_title('Document Distribution (Empty)')
    
    # 3. Metadata fields heatmap
    metadata_matrix = []
    all_fields = set()
    for collection in schema_info['collections']:
        all_fields.update(collection['metadata_fields'])
    
    all_fields = sorted(list(all_fields))
    
    if all_fields:
        for collection in schema_info['collections']:
            row = [1 if field in collection['metadata_fields'] else 0 for field in all_fields]
            metadata_matrix.append(row)
        
        if metadata_matrix:
            df_metadata = pd.DataFrame(metadata_matrix, 
                                     index=collection_names, 
                                     columns=all_fields)
            sns.heatmap(df_metadata, annot=True, cmap='Blues', ax=ax3, 
                       cbar_kws={'label': 'Field Present'})
            ax3.set_title('Metadata Fields by Collection')
            ax3.tick_params(axis='x', rotation=45)
        else:
            ax3.text(0.5, 0.5, 'No metadata fields found', ha='center', va='center')
            ax3.set_title('Metadata Fields (None Found)')
    else:
        ax3.text(0.5, 0.5, 'No metadata fields found', ha='center', va='center')
        ax3.set_title('Metadata Fields (None Found)')
    
    # 4. Summary statistics table
    ax4.axis('tight')
    ax4.axis('off')
    
    summary_data = [
        ['Total Collections', len(schema_info['collections'])],
        ['Total Documents', schema_info['total_documents']],
        ['Analysis Time', schema_info['analysis_timestamp'][:19]],
        ['Avg Docs/Collection', f"{schema_info['total_documents']/len(schema_info['collections']):.1f}" if schema_info['collections'] else '0']
    ]
    
    table = ax4.table(cellText=summary_data,
                     colLabels=['Metric', 'Value'],
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    ax4.set_title('Summary Statistics')
    
    plt.tight_layout()
    
    # Save plot
    output_path = os.path.join(viz_dir, 'chroma_overview.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Collection overview saved to: {output_path}")
    plt.close()

def create_document_analysis_plot(collection_data, viz_dir):
    """Create detailed document analysis plots"""
    if not collection_data:
        print("No collection data for document analysis")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Document Content Analysis', fontsize=16, fontweight='bold')
    
    # Prepare data for all collections
    all_doc_lengths = []
    collection_labels = []
    id_pattern_data = {}
    
    for coll_name, data in collection_data.items():
        # Document lengths
        if data['documents']:
            lengths = [len(doc) if doc else 0 for doc in data['documents']]
            all_doc_lengths.extend(lengths)
            collection_labels.extend([coll_name] * len(lengths))
        
        # ID patterns
        if data['ids']:
            for doc_id in data['ids']:
                pattern = doc_id.split('_')[0] if '_' in doc_id else 'other'
                if pattern not in id_pattern_data:
                    id_pattern_data[pattern] = 0
                id_pattern_data[pattern] += 1
    
    # 1. Document length distribution
    if all_doc_lengths:
        df_lengths = pd.DataFrame({
            'length': all_doc_lengths,
            'collection': collection_labels
        })
        
        sns.boxplot(data=df_lengths, x='collection', y='length', ax=axes[0,0])
        axes[0,0].set_title('Document Length Distribution by Collection')
        axes[0,0].set_xlabel('Collection')
        axes[0,0].set_ylabel('Document Length (characters)')
        axes[0,0].tick_params(axis='x', rotation=45)
    else:
        axes[0,0].text(0.5, 0.5, 'No documents found', ha='center', va='center')
        axes[0,0].set_title('Document Lengths (No Data)')
    
    # 2. Document length histogram
    if all_doc_lengths:
        axes[0,1].hist(all_doc_lengths, bins=30, alpha=0.7, edgecolor='black')
        axes[0,1].set_title('Overall Document Length Distribution')
        axes[0,1].set_xlabel('Document Length (characters)')
        axes[0,1].set_ylabel('Frequency')
        axes[0,1].axvline(np.mean(all_doc_lengths), color='red', linestyle='--', 
                         label=f'Mean: {np.mean(all_doc_lengths):.0f}')
        axes[0,1].legend()
    else:
        axes[0,1].text(0.5, 0.5, 'No documents found', ha='center', va='center')
        axes[0,1].set_title('Document Length Histogram (No Data)')
    
    # 3. ID pattern distribution
    if id_pattern_data:
        patterns = list(id_pattern_data.keys())
        counts = list(id_pattern_data.values())
        
        bars = axes[1,0].bar(patterns, counts, color=sns.color_palette("Set2", len(patterns)))
        axes[1,0].set_title('Document ID Patterns')
        axes[1,0].set_xlabel('ID Pattern')
        axes[1,0].set_ylabel('Count')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            axes[1,0].text(bar.get_x() + bar.get_width()/2., height,
                          f'{int(height)}', ha='center', va='bottom')
    else:
        axes[1,0].text(0.5, 0.5, 'No ID patterns found', ha='center', va='center')
        axes[1,0].set_title('ID Patterns (No Data)')
    
    # 4. Collection size comparison
    collection_sizes = [data['count'] for data in collection_data.values()]
    collection_names = list(collection_data.keys())
    
    if collection_sizes:
        bars = axes[1,1].bar(collection_names, collection_sizes, 
                           color=sns.color_palette("viridis", len(collection_names)))
        axes[1,1].set_title('Collection Size Comparison')
        axes[1,1].set_xlabel('Collection')
        axes[1,1].set_ylabel('Document Count')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            axes[1,1].text(bar.get_x() + bar.get_width()/2., height,
                          f'{int(height)}', ha='center', va='bottom')
    else:
        axes[1,1].text(0.5, 0.5, 'No collections found', ha='center', va='center')
        axes[1,1].set_title('Collection Sizes (No Data)')
    
    plt.tight_layout()
    
    # Save plot
    output_path = os.path.join(viz_dir, 'document_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Document analysis saved to: {output_path}")
    plt.close()

def create_metadata_analysis_plot(collection_data, viz_dir):
    """Create metadata-specific analysis plots"""
    if not collection_data:
        print("No collection data for metadata analysis")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Metadata Analysis', fontsize=16, fontweight='bold')
    
    # Collect all metadata
    all_metadata = {}
    metadata_by_collection = {}
    
    for coll_name, data in collection_data.items():
        metadata_by_collection[coll_name] = {}
        if data['metadatas']:
            for metadata in data['metadatas']:
                if metadata:
                    for key, value in metadata.items():
                        # Global metadata tracking
                        if key not in all_metadata:
                            all_metadata[key] = []
                        all_metadata[key].append(value)
                        
                        # Collection-specific metadata tracking
                        if key not in metadata_by_collection[coll_name]:
                            metadata_by_collection[coll_name][key] = []
                        metadata_by_collection[coll_name][key].append(value)
    
    # 1. Metadata field frequency across collections
    field_frequency = {}
    for coll_name, metadata in metadata_by_collection.items():
        for field in metadata.keys():
            if field not in field_frequency:
                field_frequency[field] = 0
            field_frequency[field] += 1
    
    if field_frequency:
        fields = list(field_frequency.keys())
        frequencies = list(field_frequency.values())
        
        bars = axes[0,0].bar(fields, frequencies, color=sns.color_palette("plasma", len(fields)))
        axes[0,0].set_title('Metadata Field Frequency Across Collections')
        axes[0,0].set_xlabel('Metadata Field')
        axes[0,0].set_ylabel('Number of Collections')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            axes[0,0].text(bar.get_x() + bar.get_width()/2., height,
                          f'{int(height)}', ha='center', va='bottom')
    else:
        axes[0,0].text(0.5, 0.5, 'No metadata fields found', ha='center', va='center')
        axes[0,0].set_title('Metadata Field Frequency (No Data)')
    
    # 2. Unique values per metadata field
    if all_metadata:
        field_unique_counts = {field: len(set(values)) for field, values in all_metadata.items()}
        
        fields = list(field_unique_counts.keys())
        unique_counts = list(field_unique_counts.values())
        
        bars = axes[0,1].bar(fields, unique_counts, color=sns.color_palette("coolwarm", len(fields)))
        axes[0,1].set_title('Unique Values per Metadata Field')
        axes[0,1].set_xlabel('Metadata Field')
        axes[0,1].set_ylabel('Number of Unique Values')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            axes[0,1].text(bar.get_x() + bar.get_width()/2., height,
                          f'{int(height)}', ha='center', va='bottom')
    else:
        axes[0,1].text(0.5, 0.5, 'No metadata found', ha='center', va='center')
        axes[0,1].set_title('Unique Values per Field (No Data)')
    
    # 3. Metadata completeness heatmap
    if metadata_by_collection:
        # Create completeness matrix
        all_fields = set()
        for metadata in metadata_by_collection.values():
            all_fields.update(metadata.keys())
        
        all_fields = sorted(list(all_fields))
        completeness_matrix = []
        collection_names = []
        
        for coll_name, metadata in metadata_by_collection.items():
            collection_names.append(coll_name)
            row = []
            for field in all_fields:
                if field in metadata:
                    # Calculate completeness percentage
                    total_docs = collection_data[coll_name]['count']
                    field_count = len(metadata[field])
                    completeness = (field_count / total_docs * 100) if total_docs > 0 else 0
                    row.append(completeness)
                else:
                    row.append(0)
            completeness_matrix.append(row)
        
        if completeness_matrix and all_fields:
            df_completeness = pd.DataFrame(completeness_matrix,
                                         index=collection_names,
                                         columns=all_fields)
            sns.heatmap(df_completeness, annot=True, fmt='.1f', cmap='YlOrRd', ax=axes[1,0],
                       cbar_kws={'label': 'Completeness (%)'})
            axes[1,0].set_title('Metadata Field Completeness by Collection')
            axes[1,0].tick_params(axis='x', rotation=45)
        else:
            axes[1,0].text(0.5, 0.5, 'No metadata to analyze', ha='center', va='center')
            axes[1,0].set_title('Metadata Completeness (No Data)')
    else:
        axes[1,0].text(0.5, 0.5, 'No metadata found', ha='center', va='center')
        axes[1,0].set_title('Metadata Completeness (No Data)')
    
    # 4. Metadata value distribution (for numeric fields)
    axes[1,1].axis('off')
    
    # Find numeric metadata fields and create summary
    numeric_summary = []
    for field, values in all_metadata.items():
        try:
            # Try to convert to numeric
            numeric_values = []
            for v in values:
                if isinstance(v, (int, float)):
                    numeric_values.append(v)
                elif isinstance(v, str) and v.isdigit():
                    numeric_values.append(int(v))
            
            if numeric_values:
                numeric_summary.append([
                    field,
                    len(numeric_values),
                    f"{np.mean(numeric_values):.1f}",
                    f"{np.std(numeric_values):.1f}"
                ])
        except:
            continue
    
    if numeric_summary:
        table = axes[1,1].table(cellText=numeric_summary,
                               colLabels=['Field', 'Count', 'Mean', 'Std Dev'],
                               cellLoc='center',
                               loc='center',
                               bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        axes[1,1].set_title('Numeric Metadata Statistics')
    else:
        axes[1,1].text(0.5, 0.5, 'No numeric metadata fields found', ha='center', va='center')
        axes[1,1].set_title('Numeric Metadata (None Found)')
    
    plt.tight_layout()
    
    # Save plot
    output_path = os.path.join(viz_dir, 'metadata_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Metadata analysis saved to: {output_path}")
    plt.close()

def save_schema_report(schema_info, collection_data, viz_dir):
    """Save detailed schema report as JSON and text"""
    if not schema_info:
        print("No schema information to save")
        return
    
    # Save JSON report
    json_path = os.path.join(viz_dir, 'chroma_schema_report.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(schema_info, f, indent=2, ensure_ascii=False)
    print(f"Schema report (JSON) saved to: {json_path}")
    
    # Save text report
    txt_path = os.path.join(viz_dir, 'chroma_schema_report.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("ChromaDB Schema Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Analysis Timestamp: {schema_info['analysis_timestamp']}\n")
        f.write(f"Total Collections: {len(schema_info['collections'])}\n")
        f.write(f"Total Documents: {schema_info['total_documents']}\n\n")
        
        for i, collection in enumerate(schema_info['collections'], 1):
            f.write(f"{i}. Collection: {collection['name']}\n")
            f.write(f"   Document Count: {collection['document_count']}\n")
            f.write(f"   Metadata Fields: {', '.join(collection['metadata_fields']) if collection['metadata_fields'] else 'None'}\n")
            f.write(f"   ID Patterns: {collection['id_patterns']}\n")
            if collection['document_lengths']:
                f.write(f"   Document Length Stats:\n")
                f.write(f"     - Min: {min(collection['document_lengths'])}\n")
                f.write(f"     - Max: {max(collection['document_lengths'])}\n")
                f.write(f"     - Mean: {np.mean(collection['document_lengths']):.1f}\n")
                f.write(f"     - Median: {np.median(collection['document_lengths']):.1f}\n")
            f.write(f"   Sample IDs: {', '.join(collection['sample_ids'][:3])}\n\n")
    
    print(f"Schema report (TXT) saved to: {txt_path}")

def main():
    """Main function to run ChromaDB analysis and create visualizations"""
    print("ChromaDB Schema Analysis and Visualization Tool")
    print("=" * 50)
    
    # Set up visualization directory
    viz_dir = setup_visualization_dir()
    print(f"Visualizations will be saved to: {viz_dir}")
    
    # Configure matplotlib and seaborn
    plt.style.use('default')
    sns.set_palette("husl")
    
    try:
        # Analyze ChromaDB
        print("\n1. Analyzing ChromaDB collections...")
        schema_info, collection_data = analyze_chroma_collections()
        
        if not schema_info:
            print("Failed to analyze ChromaDB. Please check your database connection.")
            return
        
        # Create visualizations
        print("\n2. Creating collection overview visualization...")
        create_collection_overview_plot(schema_info, viz_dir)
        
        print("\n3. Creating document analysis visualization...")
        create_document_analysis_plot(collection_data, viz_dir)
        
        print("\n4. Creating metadata analysis visualization...")
        create_metadata_analysis_plot(collection_data, viz_dir)
        
        # Save detailed reports
        print("\n5. Saving detailed schema reports...")
        save_schema_report(schema_info, collection_data, viz_dir)
        
        print("\n" + "=" * 50)
        print("Analysis complete! Generated files:")
        print(f"  - {viz_dir}/chroma_overview.png")
        print(f"  - {viz_dir}/document_analysis.png")
        print(f"  - {viz_dir}/metadata_analysis.png")
        print(f"  - {viz_dir}/chroma_schema_report.json")
        print(f"  - {viz_dir}/chroma_schema_report.txt")
        
        # Print summary
        print(f"\nQuick Summary:")
        print(f"  - Collections found: {len(schema_info['collections'])}")
        print(f"  - Total documents: {schema_info['total_documents']}")
        for collection in schema_info['collections']:
            print(f"    • {collection['name']}: {collection['document_count']} documents")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()