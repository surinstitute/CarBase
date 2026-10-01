<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

const search = ref('')
const quickFilters = [
	{ label: 'SUV', bodyStyle: 'suv' },
	{ label: 'Truck', bodyStyle: 'pickup' },
	{ label: 'Sedán', bodyStyle: 'sedan' },
	{ label: 'Hatchback', bodyStyle: 'hatchback' }
]
const powertrainFilters = [
	{ label: 'Combustión', powertrainType: 'combustion' },
	{ label: 'Híbrido', powertrainType: 'hybrid' },
	{ label: 'Híbrido enchufable', powertrainType: 'plug_in_hybrid' },
	{ label: 'Eléctrico', powertrainType: 'electric' }
]

function browseCatalog() {
	navigateTo({ path: '/models', query: search.value.trim() ? { q: search.value.trim() } : undefined })
}

function browseBodyStyle(bodyStyle: string) {
	navigateTo({ path: '/models', query: { body_style: bodyStyle } })
}

function browsePowertrain(powertrainType: string) {
	navigateTo({ path: '/models', query: { powertrain_type: powertrainType } })
}

function browseAssemblyCountry(country: string) {
	navigateTo({ path: '/models', query: { assembly_country: country } })
}
</script>

<template>
	<section class="border-b bg-muted/30">
		<div class="mx-auto w-full max-w-6xl px-4 py-16 sm:py-24">
			<div class="max-w-3xl space-y-6">
				<Badge variant="secondary">Catálogo de vehículos</Badge>
				<div class="space-y-3">
					<h1 class="text-4xl font-bold tracking-tight sm:text-5xl">Autos y Datos Abiertos</h1>
					<p class="max-w-2xl text-lg text-muted-foreground">Compara modelosy sistemas de propulsión para decidir mejor.</p>
				</div>
				<Card class="max-w-2xl">
					<CardContent class="p-4 sm:p-6">
						<form class="flex flex-col gap-3 sm:flex-row" @submit.prevent="browseCatalog">
							<label for="vehicle-search" class="sr-only">Buscar marca, modelo o versión</label>
							<Input id="vehicle-search" v-model="search" placeholder="Busca marca, modelo o versión" class="flex-1" />
							<Button type="submit"><Icon name="tabler:search" aria-hidden="true" />Buscar</Button>
						</form>
					</CardContent>
				</Card>
				<div class="flex flex-wrap items-center gap-2">
					<span class="mr-1 text-sm text-muted-foreground">Explorar por carrocería</span>
					<Button v-for="filter in quickFilters" :key="filter.bodyStyle" type="button" variant="outline" @click="browseBodyStyle(filter.bodyStyle)">
						{{ filter.label }}
					</Button>
				</div>
				<div class="flex flex-wrap items-center gap-2">
					<span class="mr-1 text-sm text-muted-foreground">Explorar por mecánica</span>
					<Button v-for="filter in powertrainFilters" :key="filter.powertrainType" type="button" variant="outline" @click="browsePowertrain(filter.powertrainType)">
						{{ filter.label }}
					</Button>
				</div>
				<div class="flex flex-wrap items-center gap-2">
					<span class="mr-1 text-sm text-muted-foreground">Explorar por origen</span>
					<Button type="button" variant="outline" @click="browseAssemblyCountry('MX')">Hecho en México</Button>
				</div>
			</div>
		</div>
	</section>

	<section class="mx-auto grid w-full max-w-6xl gap-4 px-4 py-10 sm:grid-cols-[1fr_auto] sm:items-center">
		<div class="space-y-2">
			<h2 class="text-xl font-semibold tracking-tight">Todo en contexto</h2>
			<p class="text-sm text-muted-foreground">Explora cada vehículo con los datos importantes a primera vista.</p>
		</div>
		<NuxtLink to="/models" class="text-sm font-medium underline underline-offset-4">Ver modelos</NuxtLink>
	</section>
</template>
