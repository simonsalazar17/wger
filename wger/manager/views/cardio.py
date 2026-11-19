# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

# wger
from wger.manager.forms import CardioLogForm
from wger.manager.models import CardioLog


@login_required
def overview(request):
    """List the current user's cardio logs and accept a new activity."""

    if request.method == 'POST':
        form = CardioLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            return redirect('manager:cardio-overview')
    else:
        form = CardioLogForm()

    return render(
        request,
        'manager/cardio/overview.html',
        {
            'form': form,
            'logs': CardioLog.objects.filter(user=request.user),
        },
    )


@login_required
def edit(request, pk):
    """Edit a cardio log owned by the current user."""

    log = get_object_or_404(CardioLog, pk=pk, user=request.user)
    form = CardioLogForm(request.POST or None, instance=log)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('manager:cardio-overview')

    return render(request, 'manager/cardio/form.html', {'form': form, 'log': log})


@login_required
def delete(request, pk):
    """Delete a cardio log owned by the current user after confirmation."""

    log = get_object_or_404(CardioLog, pk=pk, user=request.user)
    if request.method == 'POST':
        log.delete()
        return redirect('manager:cardio-overview')

    return render(request, 'manager/cardio/confirm_delete.html', {'log': log})
