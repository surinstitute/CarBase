<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

const search = ref('')

function browseCatalog() {
	navigateTo({ path: '/catalog', query: search.value.trim() ? { q: search.value.trim() } : undefined })
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
							<label for="vehicle-search" class="sr-only">Buscar marca o modelo</label>
							<Input id="vehicle-search" v-model="search" placeholder="Busca marca o modelo" class="flex-1" />
							<Button type="submit"><Icon name="tabler:search" aria-hidden="true" />Buscar</Button>
						</form>
					</CardContent>
				</Card>
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
