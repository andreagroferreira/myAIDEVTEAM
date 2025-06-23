"""
Vue.js Architect agent for CFTeam ecosystem
"""

from typing import Dict, Any, List, Optional
from crewai import Task

from src.agents.base_agent import BaseAgent, AgentConfig
from src.models import AgentRole, AgentTier
from src.tools.vue_tools import NpmTool, ViteTool, TypeScriptTool


class VueArchitect(BaseAgent):
    """Vue.js frontend architect agent"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if not config:
            config = AgentConfig(
                identifier="vue_architect",
                name="Vue.js Architect",
                role=AgentRole.VUE_ARCHITECT,
                tier=AgentTier.DEVELOPMENT,
                goal="Create efficient Vue.js interfaces with TypeScript and Vuetify",
                backstory="Frontend expert in Vue 3, TypeScript, Vuetify 3, and modern development practices",
                capabilities=[
                    "vue_architecture",
                    "component_design",
                    "state_management",
                    "typescript_implementation"
                ],
                tools=["npm", "vite", "typescript"],
                max_rpm=15,
                allow_delegation=False
            )
        
        super().__init__(config)
        
        # Initialize tools
        self.npm_tool = NpmTool()
        self.vite_tool = ViteTool()
        self.typescript_tool = TypeScriptTool()
    
    async def create_component(
        self,
        component_name: str,
        project_path: str,
        component_type: str = "composition",  # composition or options
        with_tests: bool = True
    ) -> Dict[str, Any]:
        """Create a new Vue component"""
        self.logger.info(f"Creating Vue component: {component_name}")
        
        try:
            # Component template based on type
            if component_type == "composition":
                template = f'''<template>
  <div class="{component_name.lower()}">
    <!-- {component_name} component -->
  </div>
</template>

<script setup lang="ts">
import {{ ref, computed }} from 'vue'

interface Props {{
  // Define props here
}}

const props = defineProps<Props>()

// Component logic here
const state = ref<string>('')
</script>

<style scoped>
.{component_name.lower()} {{
  /* Component styles */
}}
</style>'''
            else:
                template = f'''<template>
  <div class="{component_name.lower()}">
    <!-- {component_name} component -->
  </div>
</template>

<script lang="ts">
import {{ defineComponent }} from 'vue'

export default defineComponent({{
  name: '{component_name}',
  props: {{
    // Define props here
  }},
  setup(props) {{
    // Component logic here
    return {{
      // Exposed properties
    }}
  }}
}})
</script>

<style scoped>
.{component_name.lower()} {{
  /* Component styles */
}}
</style>'''
            
            # Test template if needed
            test_template = f'''import {{ describe, it, expect }} from 'vitest'
import {{ mount }} from '@vue/test-utils'
import {component_name} from './{component_name}.vue'

describe('{component_name}', () => {{
  it('renders properly', () => {{
    const wrapper = mount({component_name})
    expect(wrapper.exists()).toBe(true)
  }})
}})''' if with_tests else None
            
            return {
                'success': True,
                'component': component_name,
                'template': template,
                'test_template': test_template
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create component {component_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_page(
        self,
        page_name: str,
        project_path: str,
        module: Optional[str] = None,
        with_store: bool = False
    ) -> Dict[str, Any]:
        """Create a new page component"""
        self.logger.info(f"Creating page: {page_name} for module {module}")
        
        try:
            # Page template
            template = f'''<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>{page_name} Page</h1>
      </v-col>
    </v-row>
    
    <v-row>
      <!-- Page content -->
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import {{ ref, computed, onMounted }} from 'vue'
import {{ useRoute, useRouter }} from 'vue-router'
{'import { use' + module + 'Store } from "@/stores/' + module.lower() + '"' if with_store else ''}

const route = useRoute()
const router = useRouter()
{'const store = use' + module + 'Store()' if with_store else ''}

// Page state
const loading = ref(false)
const error = ref<string | null>(null)

// Lifecycle
onMounted(async () => {{
  await loadData()
}})

// Methods
async function loadData() {{
  loading.value = true
  try {{
    // Load page data
  }} catch (e) {{
    error.value = e.message
  }} finally {{
    loading.value = false
  }}
}}
</script>

<style scoped>
/* Page-specific styles */
</style>'''
            
            # Route configuration
            route_config = {
                'path': f'/{module.lower() if module else ""}/{page_name.lower()}',
                'name': f'{module if module else ""}{page_name}',
                'component': f'() => import("@/pages{"/"+module if module else ""}/{page_name}.vue")'
            }
            
            return {
                'success': True,
                'page': page_name,
                'template': template,
                'route_config': route_config
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create page {page_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }