#!/usr/bin/env python3
"""
Add HLD diagrams to system design files and remove AlgoMaster references
"""

import re
from pathlib import Path
from typing import Dict, List

def remove_algomaster_references(content: str) -> str:
    """Remove all references to AlgoMaster"""
    # Remove AlgoMaster references
    content = re.sub(r'from AlgoMaster\.io', '', content, flags=re.IGNORECASE)
    content = re.sub(r'AlgoMaster System Design Interviews', 'System Design Examples', content, flags=re.IGNORECASE)
    content = re.sub(r'AlgoMaster\.io', '', content, flags=re.IGNORECASE)
    content = re.sub(r'https://algomaster\.io/[^\s\)]+', '', content)
    # Remove references in README files
    content = re.sub(r'from AlgoMaster\.io', '', content, flags=re.IGNORECASE)
    content = re.sub(r'This folder contains .* from AlgoMaster\.io', 'This folder contains system design examples and solutions', content, flags=re.IGNORECASE)
    return content

def extract_components_from_text(content: str) -> Dict[str, List[str]]:
    """Extract components and flows from the content"""
    components = {
        'services': [],
        'databases': [],
        'caches': [],
        'queues': [],
        'storage': [],
        'cdn': [],
        'load_balancers': []
    }
    
    # Common patterns
    service_patterns = [
        r'(\w+)\s+Service',
        r'(\w+)\s+service',
        r'Service:\s*(\w+)',
    ]
    
    db_patterns = [
        r'(\w+)\s+Database',
        r'(\w+)\s+database',
        r'PostgreSQL|MySQL|MongoDB|Cassandra|DynamoDB|Redis|Elasticsearch'
    ]
    
    cache_patterns = [
        r'(\w+)\s+Cache',
        r'Redis|Memcached'
    ]
    
    queue_patterns = [
        r'(\w+)\s+Queue',
        r'Kafka|RabbitMQ|SQS'
    ]
    
    storage_patterns = [
        r'S3|Object Storage|Google Cloud Storage'
    ]
    
    cdn_patterns = [
        r'CDN|CloudFront|Cloudflare'
    ]
    
    lb_patterns = [
        r'Load Balancer|API Gateway'
    ]
    
    # Extract services
    for pattern in service_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        components['services'].extend([m for m in matches if m and len(m) > 2])
    
    # Extract databases
    db_matches = re.findall(r'\b(PostgreSQL|MySQL|MongoDB|Cassandra|DynamoDB|Elasticsearch)\b', content, re.IGNORECASE)
    components['databases'].extend(db_matches)
    
    # Extract caches
    cache_matches = re.findall(r'\b(Redis|Memcached)\b', content, re.IGNORECASE)
    components['caches'].extend(cache_matches)
    
    # Extract queues
    queue_matches = re.findall(r'\b(Kafka|RabbitMQ|SQS)\b', content, re.IGNORECASE)
    components['queues'].extend(queue_matches)
    
    # Extract storage
    storage_matches = re.findall(r'\b(S3|Object Storage)\b', content, re.IGNORECASE)
    components['storage'].extend(storage_matches)
    
    # Extract CDN
    cdn_matches = re.findall(r'\b(CDN|CloudFront|Cloudflare)\b', content, re.IGNORECASE)
    components['cdn'].extend(cdn_matches)
    
    # Extract load balancers
    lb_matches = re.findall(r'\b(Load Balancer|API Gateway)\b', content, re.IGNORECASE)
    components['load_balancers'].extend(lb_matches)
    
    # Deduplicate
    for key in components:
        components[key] = list(set(components[key]))
    
    return components

def generate_hld_diagram(content: str, title: str) -> str:
    """Generate a Mermaid HLD diagram based on content"""
    components = extract_components_from_text(content)
    
    # Build diagram
    diagram = "```mermaid\n"
    diagram += "graph TB\n"
    diagram += "    subgraph Clients\n"
    diagram += "        Web[Web Browser]\n"
    diagram += "        Mobile[Mobile App]\n"
    diagram += "    end\n\n"
    
    # Load balancer
    if components['load_balancers']:
        diagram += "    subgraph Load Balancing\n"
        diagram += "        LB[Load Balancer]\n"
        diagram += "    end\n\n"
    
    # Services
    if components['services']:
        diagram += "    subgraph Application Services\n"
        for i, service in enumerate(components['services'][:5], 1):  # Limit to 5
            service_name = service.replace(' ', '')
            diagram += f"        S{i}[{service} Service]\n"
        diagram += "    end\n\n"
    
    # Databases
    if components['databases']:
        diagram += "    subgraph Data Storage\n"
        for db in components['databases'][:3]:  # Limit to 3
            db_name = db.replace(' ', '')
            diagram += f"        DB{db_name}[{db}]\n"
        diagram += "    end\n\n"
    
    # Caches
    if components['caches']:
        diagram += "    subgraph Caching Layer\n"
        for cache in components['caches']:
            cache_name = cache.replace(' ', '')
            diagram += f"        Cache{cache_name}[{cache}]\n"
        diagram += "    end\n\n"
    
    # Queues
    if components['queues']:
        diagram += "    subgraph Message Queue\n"
        for queue in components['queues']:
            queue_name = queue.replace(' ', '')
            diagram += f"        Queue{queue_name}[{queue}]\n"
        diagram += "    end\n\n"
    
    # Storage
    if components['storage']:
        diagram += "    subgraph Object Storage\n"
        for storage in components['storage']:
            storage_name = storage.replace(' ', '')
            diagram += f"        Storage{storage_name}[{storage}]\n"
        diagram += "    end\n\n"
    
    # CDN
    if components['cdn']:
        diagram += "    subgraph CDNLayer\n"
        diagram += "        CDNNode[Content Delivery Network]\n"
        diagram += "    end\n\n"
    
    # Connections
    diagram += "    Web --> LB\n"
    diagram += "    Mobile --> LB\n"
    
    if components['load_balancers']:
        if components['services']:
            for i in range(1, min(len(components['services']), 5) + 1):
                diagram += f"    LB --> S{i}\n"
    
    if components['services']:
        for i in range(1, min(len(components['services']), 5) + 1):
            if components['databases']:
                for db in components['databases'][:2]:
                    db_name = db.replace(' ', '').replace('-', '')
                    diagram += f"    S{i} --> DB{db_name}\n"
            if components['caches']:
                for cache in components['caches']:
                    cache_name = cache.replace(' ', '').replace('-', '')
                    diagram += f"    S{i} --> Cache{cache_name}\n"
            if components['queues']:
                for queue in components['queues']:
                    queue_name = queue.replace(' ', '').replace('-', '')
                    diagram += f"    S{i} --> Queue{queue_name}\n"
    
    if components['storage']:
        for storage in components['storage']:
            storage_name = storage.replace(' ', '').replace('-', '')
            if components['services']:
                diagram += f"    S1 --> Storage{storage_name}\n"
    
    if components['cdn']:
        if components['storage']:
            for storage in components['storage']:
                storage_name = storage.replace(' ', '').replace('-', '')
                diagram += f"    Storage{storage_name} --> CDNNode\n"
        diagram += "    CDNNode --> Web\n"
        diagram += "    CDNNode --> Mobile\n"
    
    diagram += "```\n"
    
    return diagram

def add_hld_to_file(filepath: Path):
    """Add HLD diagram to a file"""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        # Remove AlgoMaster references
        content = remove_algomaster_references(content)
        
        # Check if HLD section exists (section 3 or 4, Design or Architecture)
        hld_pattern = r'#\s*[34]\.?\s*High[\s-]?Level\s+(Design|Architecture)|##\s*[34]\.?\s*High[\s-]?Level\s+(Design|Architecture)'
        hld_match = re.search(hld_pattern, content, re.IGNORECASE)
        
        if hld_match:
            # Find the position after HLD header
            hld_pos = hld_match.end()
            
            # Remove ALL existing mermaid diagrams in the HLD section
            # Find all mermaid blocks after HLD header
            section_content = content[hld_pos:]
            # More precise pattern to match complete mermaid blocks
            mermaid_pattern = r'```mermaid\n.*?```\n'
            matches = list(re.finditer(mermaid_pattern, section_content, re.DOTALL))
            if matches:
                # Remove all mermaid blocks (in reverse order to maintain positions)
                for match in reversed(matches):
                    start = hld_pos + match.start()
                    end = hld_pos + match.end()
                    # Check what's before and after to avoid corruption
                    before_text = content[max(0, start-20):start]
                    after_text = content[end:min(len(content), end+20)]
                    # Only remove if it's a proper mermaid block
                    if '```mermaid' in before_text[-20:] or content[start:start+11] == '```mermaid':
                        content = content[:start] + content[end:]
                # Clean up any corrupted remnants
                content = re.sub(r'```me[^`]*mermai[^`]*', '', content)
                content = re.sub(r'\n{4,}', '\n\n\n', content)
                insert_pos = hld_pos + 50  # Insert after header
                print(f"  🔄 {filepath.name}: Removed {len(matches)} old diagram(s)")
            
            # Find next section (usually starts with ##)
            next_section = re.search(r'\n##\s+\d+\.', content[hld_pos:])
            insert_pos = hld_pos + (next_section.start() if next_section else 200)
            
            # Generate diagram
            title = filepath.stem.replace('design-', '').replace('-', ' ').title()
            diagram = generate_hld_diagram(content, title)
            
            # Insert diagram
            before = content[:insert_pos]
            after = content[insert_pos:]
            
            # Add diagram with spacing
            new_content = before + "\n\n" + diagram + "\n\n" + after
            
            filepath.write_text(new_content, encoding='utf-8')
            print(f"  ✅ {filepath.name}: Added HLD diagram")
        else:
            print(f"  ⚠️  {filepath.name}: No HLD section found")
            filepath.write_text(content, encoding='utf-8')
            
    except Exception as e:
        print(f"  ❌ {filepath.name}: Error - {e}")

def main():
    """Process all design files"""
    base_dir = Path('system-design/system-design-examples')
    
    # Process design problems
    design_dir = base_dir / '01-design-problems'
    md_files = list(design_dir.glob('*.md'))
    md_files = [f for f in md_files if f.name != 'README.md']
    
    print(f"Processing {len(md_files)} design files...\n")
    
    for md_file in sorted(md_files):
        add_hld_to_file(md_file)
    
    # Update README files
    readme_files = [
        base_dir / 'README.md',
        base_dir / '01-design-problems' / 'README.md',
        base_dir / '02-technologies' / 'README.md',
        base_dir / '03-concepts' / 'README.md',
        base_dir / '04-prep' / 'README.md',
    ]
    
    print("\nUpdating README files...")
    for readme_file in readme_files:
        if readme_file.exists():
            try:
                content = readme_file.read_text(encoding='utf-8')
                content = remove_algomaster_references(content)
                readme_file.write_text(content, encoding='utf-8')
                print(f"  ✅ Updated {readme_file.name}")
            except Exception as e:
                print(f"  ❌ Error updating {readme_file.name}: {e}")
    
    print("\n✅ Done!")

if __name__ == "__main__":
    main()
