/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2011-2016 OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

\*---------------------------------------------------------------------------*/

#include "inletOutletAdvectiveFvPatchField.H"
#include "addToRunTimeSelectionTable.H"
#include "fvPatchFieldMapper.H"
#include "volFields.H"
#include "EulerDdtScheme.H"
#include "CrankNicolsonDdtScheme.H"
#include "backwardDdtScheme.H"
#include "localEulerDdtScheme.H"


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

template<class Type>
Foam::inletOutletAdvectiveFvPatchField<Type>::inletOutletAdvectiveFvPatchField
(
    const fvPatch& p,
    const DimensionedField<Type, volMesh>& iF
)
:
    advectiveFvPatchField<Type>(p, iF)
{
    this->refValue() = Zero;
    this->refGrad() = Zero;
    this->valueFraction() = 0.0;
}


template<class Type>
Foam::inletOutletAdvectiveFvPatchField<Type>::inletOutletAdvectiveFvPatchField
(
    const inletOutletAdvectiveFvPatchField& ptf,
    const fvPatch& p,
    const DimensionedField<Type, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
:
    advectiveFvPatchField<Type>(ptf, p, iF, mapper)
{}


template<class Type>
Foam::inletOutletAdvectiveFvPatchField<Type>::inletOutletAdvectiveFvPatchField
(
    const fvPatch& p,
    const DimensionedField<Type, volMesh>& iF,
    const dictionary& dict
)
:
    advectiveFvPatchField<Type>(p, iF, dict)
{
    inletValue_ = dict.lookupType<Type>("inletValue");
}


template<class Type>
Foam::inletOutletAdvectiveFvPatchField<Type>::inletOutletAdvectiveFvPatchField
(
    const inletOutletAdvectiveFvPatchField& ptpsf
)
:
    advectiveFvPatchField<Type>(ptpsf)
{}


template<class Type>
Foam::inletOutletAdvectiveFvPatchField<Type>::inletOutletAdvectiveFvPatchField
(
    const inletOutletAdvectiveFvPatchField& ptpsf,
    const DimensionedField<Type, volMesh>& iF
)
:
    advectiveFvPatchField<Type>(ptpsf, iF)
{}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //


template<class Type>
void Foam::inletOutletAdvectiveFvPatchField<Type>::updateCoeffs()
{
    if (this->updated())
    {
        return;
    }

    advectiveFvPatchField<Type>::updateCoeffs();

    Field<Type>& refVal  =  this->refValue();
    scalarField& valFrac =  this->valueFraction();

    const Field<scalar>& phip =
        this->patch().template lookupPatchField<surfaceScalarField, scalar>
        (
            this->phiName_
        );
    
    scalarField inflowIndicator = 1.0 - pos0(phip);

    //Phi_face = valFrac * Phi_ref + (1-valFrac)[Phi_cell + distance*gradPhi_ref]
    refVal  = inflowIndicator * inletValue_ + (1.0 - inflowIndicator) * refVal;
    valFrac = inflowIndicator + (1.0 - inflowIndicator) * valFrac;
}


template<class Type>
void Foam::inletOutletAdvectiveFvPatchField<Type>::write(Ostream& os) const
{
    advectiveFvPatchField<Type>::write(os);
}


// ************************************************************************* //
